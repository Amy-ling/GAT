
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# 從本機 App 導入 models 和 forms
from .models import Item, ItemImage, ItemTaken
from .forms import ItemForm

# 【關鍵修改 1】從 logs App 導入新的日誌服務
from logs.services import create_log


# --- 物品列表與交易歷史 ---

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q # 引入 Q 物件

# 從本機 App 導入 models 和 forms
from .models import Item, ItemImage, ItemTaken
from .forms import ItemForm

# 【關鍵修改 1】從 logs App 導入新的日誌服務
from logs.services import create_log


# --- 物品列表與交易歷史 ---

def user_main_view(request):
    """
    普通用戶登入後的主頁，顯示所有可領取的物品。
    現在支援分類篩選和關鍵字搜尋。
    """
    # 獲取所有分類和當前選擇的分類
    categories = Item.ItemTypeChoices.choices
    selected_category = request.GET.get('category')
    query = request.GET.get('q')

    # 基本查詢集
    if request.user.is_authenticated:
        create_log(request.user, "Accessed user main portal")
        available_items = Item.objects.filter(item_state='available')
    else:
        available_items = Item.objects.filter(item_state='available')

    # 根據分類篩選
    if selected_category:
        available_items = available_items.filter(item_type=selected_category)

    # 根據關鍵字搜尋
    if query:
        available_items = available_items.filter(
            Q(item_name__icontains=query) | Q(description__icontains=query)
        )

    context = {
        'items': available_items.order_by('-give_date'),
        'categories': categories,
        'selected_category': selected_category,
        'query': query, # 將搜尋關鍵字傳到範本
        'guest': not request.user.is_authenticated,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "items/_item_list.html", context)

    return render(request, "items/user_main.html", context)


@login_required
def my_history_view(request):
    """
    顯示使用者的個人交易歷史。
    """
    # 查詢目前使用者 "拿取" 的物品紀錄
    my_taken_items = ItemTaken.objects.filter(take_user=request.user).order_by('-take_date')

    # 查詢目前使用者 "給予" 且 "已被取走" 的物品紀錄
    my_given_items_taken = ItemTaken.objects.filter(item_id__give_user=request.user).order_by('-take_date')

    # 查詢目前使用者 "給予" 且 "還可領取" 的物品
    my_given_items_available = Item.objects.filter(give_user=request.user, item_state='available').order_by(
        '-give_date')

    context = {
        'my_taken_items': my_taken_items,
        'my_given_items_taken': my_given_items_taken,
        'my_given_items_available': my_given_items_available,
    }
    # 注意：模板路徑已更新
    return render(request, 'items/my_history.html', context)


# --- 物品的增、刪、改、查 ---

@login_required
def give_item_view(request):
    """
    處理使用者 "給予" 物品的表單和邏輯。
    """
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.give_user = request.user
            item.save()

            # 處理多張圖片上傳
            images = request.FILES.getlist('item_image')
            for image in images:
                ItemImage.objects.create(item_id=item, item_image=image)

            # --- 【關鍵修改 2】使用新的日誌服務 ---
            log_action_msg = f"Gave item: '{item.item_name}' [ID:{item.id}]"
            create_log(request.user, action=log_action_msg)

            messages.success(request, '你的物品已成功發佈！')
            # 注意：URL 重定向已更新
            return redirect('items:my_history')
        else:
            create_log(request.user, action="Give item form invalid", result="failure")
            messages.warning(request, '表單內容有誤，請檢查後再試。')
    else:
        form = ItemForm()

    # 注意：模板路徑已更新
    return render(request, 'items/give_item.html', {'form': form})


@login_required
def take_item_view(request, item_id):
    item_to_take = get_object_or_404(Item, id=item_id)

    # 確保物品是可領取狀態
    if item_to_take.item_state != 'available':
        messages.warning(request, "這個物品已經被取走或已下架。")
        return redirect('items:user_main')  # 導向物品列表

    # 使用者不能拿自己的物品
    if item_to_take.give_user == request.user:
        messages.error(request, "你不能拿取自己的物品。")
        return redirect('items:user_main')

    if request.method == 'POST':
        # 更新物品狀態
        item_to_take.item_state = 'taken'
        item_to_take.save(update_fields=['item_state'])

        ItemTaken.objects.create(item_id=item_to_take, take_user=request.user)

        # --- 【關鍵修改 2】使用新的日誌服務 ---
        log_action_msg = f"Took item: '{item_to_take.item_name}' [ID:{item_to_take.id}] from user '{item_to_take.give_user.username}'"
        create_log(request.user, action=log_action_msg)

        messages.success(request, f'你已成功取走物品 "{item_to_take.item_name}"。')
        return redirect('items:my_history')

    context = {'item': item_to_take}
    return render(request, 'items/confirm_take_item.html', context)


@login_required
def edit_item_view(request, item_id):
    """
    處理使用者編輯自己物品的邏輯。
    """
    item = get_object_or_404(Item, id=item_id, give_user=request.user)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            edited_item = form.save()

            # 處理圖片更新...
            if 'item_image' in request.FILES:
                # Delete old images
                ItemImage.objects.filter(item_id=edited_item).delete()
                # Add new images
                images = request.FILES.getlist('item_image')
                for image in images:
                    ItemImage.objects.create(item_id=edited_item, item_image=image)

            # --- 【關鍵修改 2】使用新的日誌服務 ---
            log_action_msg = f"Edited item: '{edited_item.item_name}' [ID:{edited_item.id}]"
            create_log(request.user, action=log_action_msg)

            messages.success(request, '物品資料已更新！')
            return redirect('items:my_history')
    else:
        form = ItemForm(instance=item)

    context = {'form': form, 'item': item}
    # 注意：模板路徑已更新
    return render(request, 'items/edit_item.html', context)


@login_required
def delete_item_view(request, item_id):
    """
    處理使用者刪除自己物品的邏輯。
    """
    item_to_delete = get_object_or_404(Item, id=item_id, give_user=request.user)

    if request.method == 'POST':
        item_name = item_to_delete.item_name
        item_to_delete.delete()

        # --- 【關鍵修改 2】使用新的日誌服務 ---
        log_action_msg = f"Deleted item: '{item_name}' [ID:{item_id}]"
        create_log(request.user, action=log_action_msg)

        messages.success(request, f'物品 "{item_name}" 已成功刪除。')
        return redirect('items:my_history')

    context = {'item': item_to_delete}
    # 注意：模板路徑已更新
    return render(request, 'items/delete_item_confirm.html', context)