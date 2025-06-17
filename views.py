from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
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


##############################################
# set sessions and check if system admin
##############################################
@login_required
def gat_portal(request):
    uid = request.user.id
    up = UserProfile.objects.get(id=uid)
    request.session['uid'] = uid
    request.session['uname'] = up.name
    #save to logbook
    logbook_save(uid, 'login', 'success')
    #check user profile if is admin
    if up.is_admin:
        request.session['is_admin'] = True
        return render(request, "gat_app/sysadmin_main.html")
    else:
        request.session['is_admin'] = False
        return render(request, "gat_app/user_main.html")


##############################################
# block of user functions
##############################################
@login_required
def profile_view(request):
    profile = request.user.profile
    profile = request.user.profile

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.session['uname'] = profile.name
            messages.success(request, 'Your profile has been updated successfully!')
            logbook_save(request.user.id, 'user profile update', 'success')
            return redirect('profile')
        else:
            logbook_save(request.user.id, 'user profile update', 'failure')
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

            images = request.FILES.getlist('item_image')
            for image in images:
                ItemImage.objects.create(item_id=item, item_image=image)
            logbook_save(request.user.id, f'Item given [ID:{item.id}]', 'success')
            messages.success(request, 'Your item has been successfully posted!')
        else:
            logbook_save(request.user.id, f'Item give', 'failure')
        return redirect('user_history')
    else:
        form = ItemForm()

    return render(request, 'gat_app/give_item.html', {'form': form})

@login_required
def user_history_view(request):
    # Tab 1: Items the user has posted that are still available
    available_items = Item.objects.filter(
        give_user=request.user,
        item_state='available'
    ).order_by('-give_date')

    # Tab 2: Items the user posted that have been taken by others
    given_and_taken_items = Item.objects.filter(
        give_user=request.user,
        item_state='taken'
    ).order_by('-give_date')

    # Tab 3: Items the user has taken from other people
    my_taken_items = ItemTaken.objects.filter(take_user=request.user).order_by('-take_date')

    context = {
        'available_items': available_items,
        'given_and_taken_items': given_and_taken_items,
        'my_taken_items': my_taken_items,
    }
    return render(request, 'gat_app/my_history.html', context)

@login_required
def edit_item_view(request, pk):
    # Get the specific item by its primary key (pk), or show a 404 error if not found
    # Also ensure the item belongs to the logged-in user to prevent unauthorized editing
    item = get_object_or_404(Item, pk=pk, give_user=request.user)

    if request.method == 'POST':
        # Pass the instance to the form to update the existing item
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()  # Save the changes to the item

            # Handle updated images (optional: you can add logic here to delete old images)
            images = request.FILES.getlist('item_image')
            if images:
                # If new images are uploaded, you might want to clear old ones first
                ItemImage.objects.filter(item_id=item).delete()
                for image in images:
                    ItemImage.objects.create(item_id=item, item_image=image)

            messages.success(request, 'Your item has been updated successfully!')
            logbook_save(request.user.id, f'Item updated [ID:{pk}]', 'success')
        return redirect('user_history')
    else:
        # On a GET request, pre-populate the form with the item's current data
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
        messages.success(request, f'The item "{item_name}" has been successfully taken back.')
        logbook_save(request.user.id, f'Item deleted [ID:{pk}]', 'success')
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


##############################################
#block of system admin functions
##############################################
@login_required
def sysadmin_log_list(request):
    #logs = LogBook.objects.all().order_by('-log_date')
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
            return render(request, "gat_app/sysadmin_log_list.html")
    else:
        return render(request, "gat_app/sysadmin_log_list.html")

@login_required
def systemadmin_log_delete(request, pk):
    log_rec = LogBook.objects.get(pk=pk)
    log_rec.delete()
    logbook_save(request.session['uid'], "Log record delete", "success")
    return redirect("sysadmin_log_list")

@login_required
def systemadmin_reset_pwd(request):
    return render(request, "gat_app/sysadmin_reset_pwd.html")

@login_required
def user_reset_pwd(request):
#def user_reset_pwd(request, uname, new_pwd):
    if request.method == "POST":
        try:
            up = UserProfile.objects.get(phone=request.POST.get('user_phone'))
            usr = User.objects.get(id=up.id)
            #mark log message with user phone number as reference
            log_action_msg = "reset pwd [" + request.POST.get('user_phone') + "]"
            if usr:
                usr.set_password(raw_password=request.POST.get('new_pwd'))
                usr.save()
                logbook_save(request.session['uid'], log_action_msg, 'success')
                messages.success(request, 'User password reset successfully!')
                return render(request, "gat_app/sysadmin_reset_pwd.html")
            else:
                logbook_save(request.session['uid'], log_action_msg, 'failure')
                messages.success(request, 'User password reset failure!')
                return render(request, "gat_app/sysadmin_reset_pwd.html")
        except:
            logbook_save(request.session['uid'], 'reset pwd [admin]', 'failure')
            messages.success(request, 'User not found! Please try again.')
            return render(request, "gat_app/sysadmin_reset_pwd.html")
    else:
        return render(request, "gat_app/sysadmin_reset_pwd.html")
