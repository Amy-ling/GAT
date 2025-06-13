from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserProfileUpdateForm, UserLoginForm, ItemForm
from django.contrib.auth.models import User
from .models import LogBook, Item, ItemImage
from django.contrib.auth import login
from django.http import HttpResponse

# Create your views here.
def logbook_save(uid, action, result):
    LogBook.objects.create(log_action=action.upper(), log_result=result.upper(), log_user_id=uid)

def gat_index(request):
    return render(request, "gat_app/index.html")

@login_required
def gat_user_index(request):
    return render(request, "gat_app/user_main.html")

# gat_app/views.py

@login_required
def systemadmin_index(request):
    # 加入權限檢查：確保只有 is_admin=True 的使用者才能訪問
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
        messages.error(request, "You do not have permission to view this page.")
        # 如果權限不符，可以將他們導向到一般使用者的主頁或個人資料頁
        return redirect('gat_user_index')

    # 如果權限正確，才渲染管理者主頁
    return render(request, "gat_app/sysadmin_main.html")
def register_view(request):
    if request.method == 'POST':
        # Use your custom form
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # The custom save() method now handles everything
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            # Make sure 'login' is the name of your login URL pattern
            return redirect('login')
    else:
        # Use your custom form
        form = UserRegisterForm()
    return render(request, 'gat_app/register.html', {'form': form})

@login_required
def profile_view(request):
    # We get the user's profile through the related_name "profile" we set in the model
    profile = request.user.profile

    if request.method == 'POST':
        # Pass the instance to the form to update the existing profile
        form = UserProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile') # Redirect back to the profile page
    else:
        # On a GET request, pre-populate the form with the user's current profile data
        form = UserProfileUpdateForm(instance=profile)

    context = {
        'form': form
    }
    return render(request, 'gat_app/profile.html', context)

@login_required
def sysadmin_log_list(request):
    #logs = LogBook.objects.all().order_by('-log_date')
    logs = LogBook.objects.filter(log_user_id=2).order_by('-log_date')
    context = {
        'logs': logs
    }

    return render(request, "gat_app/sysadmin_log_list.html", context)

@login_required
def systemadmin_log_delete(request, pk):
    log_rec = LogBook.objects.get(pk=pk)
    log_rec.delete()
    #logbook_save(2, "Logout", "success")
    return redirect("sysadmin_log_list")

@login_required
def systemadmin_reset_pwd(request):
    return render(request, "gat_app/sysadmin_reset_pwd.html")

@login_required
def user_reset_pwd(request):
#def user_reset_pwd(request, uname, new_pwd):
    if request.method == "POST":
        print("TEST -> " + str(request.POST))
        user = User.objects.get(username=request.POST.get('uname'))
        if user:
            user.set_password(raw_password=request.POST.get('new_pwd'))
            user.save()
            return render(request, "gat_app/sysadmin_reset_pwd.html")
        else:
            return render(request, "gat_app/sysadmin_reset_pwd.html")
    else:
        return render(request, "gat_app/sysadmin_reset_pwd.html")


def login_view(request):
    # 如果使用者已經登入，就直接將他重導向，避免他們重複登入
    if request.user.is_authenticated:
        return redirect('gat_index')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(request, f'Welcome back, {user.profile.name}!')

            # gat_app/views.py -> 於 login_view 函數中

            if hasattr(user, 'profile') and user.profile.is_admin:
                # 管理者登入後，重導向到 systemadmin_index 對應的 URL
                return redirect('systemadmin_index')
            else:
                # 一般使用者登入後，重導向到 gat_user_index 對應的 URL
                return redirect('gat_user_index')
    else:
        form = UserLoginForm()

    return render(request, 'gat_app/login.html', {'form': form})

@login_required
def give_item_view(request):
    if request.method == 'POST':
        # 處理圖片上傳需要同時傳入 request.POST 和 request.FILES
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            # 先不儲存到資料庫，因為我們需要先設定 give_user
            item = form.save(commit=False)
            # 將 give_user 設定為當前登入的使用者
            item.give_user = request.user
            # 現在可以儲存 Item 物件了
            item.save()

            # 處理圖片上傳
            image = form.cleaned_data.get('item_image')
            if image:
                ItemImage.objects.create(item_id=item, item_image=image)

            messages.success(request, '你的物品已成功發佈！')
            return redirect('my_items') # 成功後重導向到首頁
    else:
        form = ItemForm()

    return render(request, 'gat_app/give_item.html', {'form': form})


@login_required
def placeholder_view(request):
    """一個通用的佔位視圖，用於尚未開發的功能。"""
    return HttpResponse("<h1>This page is under construction.</h1><a href='javascript:history.back()'>Go Back</a>")

@login_required
def my_items_view(request):
    items = Item.objects.filter(give_user=request.user).order_by('-give_date')

    context = {
        'items': items
    }
    return render(request, 'gat_app/my_items.html', context)
@login_required
def item_history_view(request):
    return HttpResponse("<h1>History Page (Under Construction)</h1>")

# 'Take Item' 連結應該連到首頁，所以不需要為它建立獨立的 view