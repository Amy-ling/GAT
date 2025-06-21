from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserProfileUpdateForm, UserLoginForm, ItemForm
from django.contrib.auth.models import User
from .models import LogBook, UserProfile, Item, ItemImage, ItemTaken
from django.shortcuts import get_object_or_404

# Create your functions here.
def logbook_save(uid, action, result):
    LogBook.objects.create(log_action=action.upper(), log_result=result.upper(), log_user_id=uid)

# Create your views here.
def gat_index(request):
    return render(request, "gat_app/index.html")

def register_view(request):
    if request.method == 'POST':
        # Use your custom form
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # The custom save() method now handles everything
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcome to Give & Take! You can now log in.')
            # Make sure 'login' is the name of your login URL pattern
            return redirect('login')
    else:
        # Use your custom form
        form = UserRegisterForm()
    return render(request, 'gat_app/register.html', {'form': form})


###################################################
# portal; set sessions and check if system admin
###################################################
@login_required
def gat_portal(request):
    uid = request.user.id
    up = UserProfile.objects.get(id=uid)
    if request.session.get('uid') != uid:
        #user just log in
        request.session['uid'] = uid
        request.session['uname'] = up.name
        request.session['phone'] = up.phone
        logbook_save(uid, 'login', 'success')
    #check user profile if is admin
    if up.is_admin:
        # i.e. system administrator
        request.session['is_admin'] = True
        # prepare admin dashboard
        total_users = UserProfile.objects.count()
        total_items = Item.objects.count()
        available_items = Item.objects.filter(item_state='available').count()
        taken_items = Item.objects.filter(item_state='taken').count()
        recent_logs = LogBook.objects.select_related('log_user__profile').order_by('-log_date')[:10]
        recent_users = UserProfile.objects.select_related('user').order_by('-user__date_joined')[:5]

        context = {
            'total_users': total_users,
            'total_items': total_items,
            'available_items': available_items,
            'taken_items': taken_items,
            'recent_logs': recent_logs,
            'recent_users': recent_users,
        }
        return render(request, "gat_app/sysadmin_main.html", context)
    else:
        # i.e. general user
        request.session['is_admin'] = False
        # prepare user dashboard
        # 1. get latest 6 available items (except own given items)
        latest_items = Item.objects.filter(
            item_state='available'
            ).exclude(
                give_user=request.user
            ).select_related('give_user__profile').prefetch_related('itemimage_set').order_by('-give_date')[:6]

        # 2. personal statistic data for items given (available)/taken
        my_available_items_count = Item.objects.filter(give_user=request.user, item_state='available').count()
        my_taken_items_count = ItemTaken.objects.filter(take_user=request.user).count()

        context = {
            'latest_items': latest_items,
            'my_available_items_count': my_available_items_count,
            'my_taken_items_count': my_taken_items_count,
        }
        return render(request, "gat_app/user_main.html", context)


##############################################
# block of user functions
##############################################
@login_required
def profile_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.session['uname'] = profile.name
            logbook_save(request.user.id, 'user profile update', 'success')
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            logbook_save(request.user.id, 'user profile update', 'failure')
            messages.warning(request, 'Your profile update failure! Please try later.')
    else:
        form = UserProfileUpdateForm(instance=profile)

    context = {
        'form': form
    }
    return render(request, 'gat_app/profile.html', context)


##############################################
#block of give & take item
##############################################
@login_required
def give_item_view(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.give_user = request.user
            item.save()

            images = form.cleaned_data.get('item_image')
            for image in images:
                ItemImage.objects.create(item_id=item, item_image=image)

            logbook_save(request.user.id, f'Item given [ID:{item.id}]', 'success')
            messages.success(request, 'Your item has been successfully posted!')
            return redirect('user_history')
        else:
            logbook_save(request.user.id, 'Item give', 'failure')
    else:
        form = ItemForm()

    return render(request, 'gat_app/give_item.html', {'form': form})

@login_required
def edit_item_view(request, pk):
    item = get_object_or_404(Item, pk=pk, give_user=request.user)

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()

            images = form.cleaned_data.get('item_image')
            if images:
                ItemImage.objects.filter(item_id=item).delete()
                for image in images:
                    ItemImage.objects.create(item_id=item, item_image=image)

            messages.success(request, 'Your item has been updated successfully!')
            logbook_save(request.user.id, f'Item updated [ID:{pk}]', 'success')
            return redirect('user_history')
    else:
        form = ItemForm(instance=item)

    context = {
        'form': form,
        'item': item
    }
    return render(request, 'gat_app/edit_item.html', context)

@login_required
def delete_item_view(request, pk):
    item = get_object_or_404(Item, pk=pk, give_user=request.user)

    if request.method == 'POST':
        item_name = item.item_name
        item.delete()
        logbook_save(request.user.id, f'Item deleted [ID:{pk}]', 'success')
        messages.success(request, f'The item "{item_name}" has been successfully taken back.')
        return redirect('user_history')

    context = {
        'item': item
    }
    return render(request, 'gat_app/delete_item_confirm.html', context)

@login_required
def take_item_view(request):
    # Get all items that are 'available' and not given by the current user
    available_items = Item.objects.filter(
        item_state='available'
    ).exclude(
        give_user=request.user
    ).order_by('-give_date')

    context = {
        'items': available_items
    }
    return render(request, 'gat_app/take_item.html', context)

@login_required
def confirm_take_item_view(request, pk):
    # Get the item the user wants to take
    item_to_take = get_object_or_404(Item, pk=pk, item_state='available')

    # Ensure users cannot take their own items
    if item_to_take.give_user == request.user:
        messages.error(request, "You cannot take your own item.")
        return redirect('take_item')

    if request.method == 'POST':
        # Update the item's state
        item_to_take.item_state = 'taken'
        item_to_take.save(update_fields=['item_state'])

        # Create a record in the ItemTaken table
        ItemTaken.objects.create(item_id=item_to_take, take_user=request.user)

        # Log the action
        logbook_save(request.user.id, f'Item taken [ID:{pk}]', 'success')
        messages.success(request, f'You have successfully taken the item "{item_to_take.item_name}".')

        # Redirect to their history page to see the newly taken item
        return redirect('user_history')

    # For a GET request, show a confirmation page
    context = {
        'item': item_to_take
    }
    return render(request, 'gat_app/confirm_take_item.html', context)

@login_required
def user_history_view(request):
    # Tab 1: Items the user has posted that are still available
    available_items = Item.objects.filter(
        give_user=request.user,
        item_state='available'
    ).order_by('-give_date')

    # Tab 2: Items the user posted that have been taken by others
    given_and_taken_items = ItemTaken.objects.filter(
        item_id__give_user=request.user
    ).select_related(
        'item_id',
        'take_user__profile'  #get back take user profile
    ).order_by('-take_date')

    # Tab 3: Items the user has taken from other people
    my_taken_items = ItemTaken.objects.filter(take_user=request.user).order_by('-take_date')

    context = {
        'available_items': available_items,
        'given_and_taken_items': given_and_taken_items,
        'my_taken_items': my_taken_items,
    }
    return render(request, 'gat_app/my_history.html', context)


##############################################
#block of system admin functions
##############################################
@login_required
def sysadmin_log_list(request):
    if request.session['is_admin']:
        if request.method == 'POST':
            try:
                up = UserProfile.objects.get(phone=request.POST['user_phone'])
                logs = LogBook.objects.filter(log_user_id=up.id).order_by('-log_date')
                context = {
                    'logs': logs,
                    'user_name': up.name,
                    'user_phone': up.phone,
                }
                return render(request, "gat_app/sysadmin_log_list.html", context)
            except:
                logbook_save(request.session['uid'], "Logbook list", "success")
                messages.warning(request, 'Input phone number: [' + request.POST['user_phone'] + '] could not be found! Please verify and try again.')
                return render(request, "gat_app/sysadmin_log_list.html")
        else:
            return render(request, "gat_app/sysadmin_log_list.html")
    else:
        logbook_save(request.user.id, f'admin page access', 'restrict')
        messages.warning(request, 'You have not permission to perform this action!!')
        return redirect('gat_portal')

@login_required
def systemadmin_log_delete(request, pk):
    if request.session['is_admin']:
        if request.method == 'GET':
            log_rec = LogBook.objects.get(pk=pk)
            log_rec.delete()
            logbook_save(request.session['uid'], "Log record delete", "success")
            messages.success(request, 'Log record has been deleted successfully!!')
        return redirect("sysadmin_log_list")
    else:
        logbook_save(request.user.id, f'admin page access', 'restrict')
        messages.warning(request, 'You have not permission to perform this action!!')
        return redirect('gat_portal')

@login_required
def systemadmin_reset_pwd(request):
    if request.session['is_admin']:
        if request.method == "POST":
            try:
                up = UserProfile.objects.get(phone=request.POST.get('user_phone'))
                if up:
                    usr = User.objects.get(id=up.id)
                    #mark log message with user phone number as reference
                    log_action_msg = "reset pwd [" + request.POST.get('user_phone') + "]"
                    if usr:
                        usr.set_password(raw_password=request.POST.get('new_pwd'))
                        usr.save()
                        logbook_save(request.session['uid'], log_action_msg, 'success')
                        messages.success(request, 'User password reset successfully!')
                    else:
                        logbook_save(request.session['uid'], log_action_msg, 'failure')
                        messages.warning(request, 'Input phone number: [' + request.POST['user_phone'] + '] could not be found! Please verify and try again.')
                else:
                    logbook_save(request.session['uid'], 'reset pwd; not found', 'failure')
                    messages.warning(request, 'Input phone number: [' + request.POST['user_phone'] + '] could not be found! Please verify and try again.')
            except:
                logbook_save(request.session['uid'], 'reset pwd; not found', 'failure')
                messages.warning(request, 'Input phone number: [' + request.POST['user_phone'] + '] could not be found! Please verify and try again.')
        return render(request, "gat_app/sysadmin_reset_pwd.html")
    else:
        logbook_save(request.user.id, f'admin page access', 'restrict')
        messages.warning(request, 'You have not permission to perform this action!!')
        return redirect('gat_portal')