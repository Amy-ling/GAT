from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserRegisterForm, UserProfileUpdateForm, UserLoginForm, AdminProfileForm, AdminPasswordChangeForm
from items.models import Item, ItemTaken, ItemImage
from items.models import Item
from django.contrib.auth.models import User
from logs.models import LogBook
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from items.views import user_main_view
from logs.services import create_log



def gat_index(request):
    if request.user.is_authenticated:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        if user_profile.is_admin:
            create_log(request.user, "Redirected to admin portal from index")
            return redirect('users:sysadmin_main')
        else:
            create_log(request.user, "Redirected to user portal from index")
            return redirect('items:user_main')  # Redirect to the main item view for users
    else:
        create_log(None, action=f"Guest accessed index from IP: {request.META.get('REMOTE_ADDR')}")
        
        # Replicate the search and filter logic from user_main_view for guests
        query = request.GET.get('q')
        category = request.GET.get('category')
        
        available_items = Item.objects.filter(item_state='available').order_by('-give_date')
        
        if query:
            available_items = available_items.filter(item_name__icontains=query)
        
        if category:
            available_items = available_items.filter(item_type=category)
            
        context = {
            'items': available_items,
            'categories': Item.ItemTypeChoices.choices,
            'selected_category': category,
            'query': query,
            'guest': True
        }
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, "items/_item_list.html", context)
        return render(request, "index.html", context)


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Use the phone number from the form for the log, as it's the username
            phone_number = form.cleaned_data.get('phone')
            create_log(user, action=f"User '{phone_number}' registered successfully")
            messages.success(request, f'Welcome to Give & Take, {phone_number}! You can now log in.')
            return redirect('users:login')
        else:
            # Log failed registration attempt
            phone_number = request.POST.get('phone', 'N/A')
            create_log(None, f"Failed registration attempt for phone: {phone_number}", "failure")
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})





@login_required
def logout_view(request):
    # Log the action before logout, as request.user will be AnonymousUser afterward
    create_log(request.user, action="Logout success")
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('users:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid():
            # Update the user's username before saving the profile
            new_phone = u_form.cleaned_data['phone']
            user = request.user
            user.username = new_phone
            user.save()
            
            u_form.save()
            create_log(request.user, action="Profile updated successfully")
            messages.success(request, '你的個人資料已更新！')
            return redirect('users:profile')
        else:
            # Log failed profile update attempt
            create_log(request.user, "Profile update failed: form invalid", "failure")
    else:
        u_form = UserProfileUpdateForm(instance=request.user.profile)

    context = {'u_form': u_form}
    return render(request, 'users/profile.html', context)


@login_required
def gat_portal(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Check if the user is an admin and redirect if necessary
    if user_profile.is_admin:
        create_log(request.user, "Redirected to admin portal from gat_portal")
        return redirect('users:sysadmin_main')

    create_log(request.user, "Accessed user portal (gat_portal)")

    given_items_count = Item.objects.filter(give_user=request.user).count()
    taken_items_count = ItemTaken.objects.filter(take_user=request.user).count()
    available_items_count = Item.objects.filter(give_user=request.user, item_state='available').count()
    
    # Get the 4 newest items, excluding the user's own items
    newest_items = Item.objects.filter(item_state='available').exclude(give_user=request.user).order_by('-give_date')[:4]

    context = {
        'given_items_count': given_items_count,
        'taken_items_count': taken_items_count,
        'available_items_count': available_items_count,
        'items': newest_items,
        'guest': False,
    }
    return render(request, "users/gat_portal.html", context)

@login_required
def sysadmin_main(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.is_admin:
        create_log(request.user, "Accessed sysadmin main page")
        
        # Card data
        total_users = User.objects.count()
        total_items = Item.objects.count()
        available_items_count = Item.objects.filter(item_state='available').count()
        taken_items_count = ItemTaken.objects.count()
        
        # Table data
        recent_users = UserProfile.objects.order_by('-user__date_joined')[:5]
        recent_logs = LogBook.objects.order_by('-log_date')[:5]

        # Chart data
        item_status_data = {
            'available': available_items_count,
            'taken': taken_items_count,
        }

        today = timezone.now().date()
        seven_days_ago = today - timedelta(days=6)
        date_range = [seven_days_ago + timedelta(days=i) for i in range(7)]

        new_users_data = []
        new_items_data = []

        for day in date_range:
            new_users_count = User.objects.filter(date_joined__date=day).count()
            new_items_count = Item.objects.filter(give_date__date=day).count()
            new_users_data.append(new_users_count)
            new_items_data.append(new_items_count)

        chart_labels = [day.strftime('%b %d') for day in date_range]

        context = {
            'total_users': total_users,
            'total_items': total_items,
            'available_items': available_items_count,
            'taken_items': taken_items_count,
            'recent_users': recent_users,
            'recent_logs': recent_logs,
            'item_status_data': item_status_data,
            'recent_activity_labels': chart_labels,
            'recent_activity_new_users': new_users_data,
            'recent_activity_new_items': new_items_data,
        }
        return render(request, "users/sysadmin_main.html", context)
    else:
        create_log(request.user, action="Admin page access denied", result="failure")
        messages.warning(request, 'You do not have permission to perform this action!')
        return redirect('items:user_main')


@login_required
def sysadmin_reset_pwd(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.is_admin:
        phone_number = request.GET.get('phone', '')
        context = {'phone_number': phone_number}

        if request.method == 'POST':
            phone_num = request.POST.get('user_phone')
            new_pwd = request.POST.get('new_pwd')
            try:
                target_profile = UserProfile.objects.get(phone=phone_num)
                target_user = target_profile.user
                target_user.set_password(new_pwd)
                target_user.save()
                log_action_msg = f"Admin '{request.user.username}' reset password for user: '{target_user.username}'"
                create_log(request.user, log_action_msg, 'success')
                messages.success(request, f"User '{target_user.username}'s password has been reset successfully!")
            except UserProfile.DoesNotExist:
                log_action_msg = f"Admin '{request.user.username}' failed to find user with phone: {phone_num}"
                create_log(request.user, log_action_msg, 'failure')
                messages.warning(request, f'Could not find user with phone number: [{phone_num}]!')
        
        return render(request, "users/sysadmin_reset_pwd.html", context)
    else:
        create_log(request.user, action="Reset password page access denied", result="failure")
        messages.warning(request, 'You do not have permission to perform this action!')
        return redirect('items:user_main')

class CustomPasswordChangeView(PasswordChangeView):
    def form_valid(self, form):
        create_log(self.request.user, "Password changed successfully")
        return super().form_valid(form)

@login_required
def admin_profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if not user_profile.is_admin:
        messages.warning(request, 'You do not have permission to perform this action!')
        return redirect('items:user_main')

    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            new_phone = form.cleaned_data['phone']
            user = request.user
            user.username = new_phone
            user.save()
            
            form.save()
            create_log(request.user, action="Admin profile updated successfully")
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:admin_profile')
        else:
            create_log(request.user, "Admin profile update failed: form invalid", "failure")
    else:
        form = AdminProfileForm(instance=request.user.profile)

    context = {'form': form}
    return render(request, 'users/admin_profile.html', context)

class AdminPasswordChangeView(PasswordChangeView):
    form_class = AdminPasswordChangeForm
    template_name = 'users/admin_password_change.html'
    success_url = reverse_lazy('users:admin_password_change_done')

    def form_valid(self, form):
        create_log(self.request.user, "Admin password changed successfully")
        return super().form_valid(form)

class AdminPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'users/admin_password_change_done.html'

@login_required
def admin_search(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if not user_profile.is_admin:
        messages.warning(request, 'You do not have permission to perform this action!')
        return redirect('items:user_main')

    query = request.GET.get('q')
    results = []
    if query:
        results = UserProfile.objects.filter(
            Q(name__icontains=query) | Q(phone__icontains=query)
        ).select_related('user')
        create_log(request.user, f"Searched for users with query: '{query}'")

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'users/admin_search_results.html', context)
