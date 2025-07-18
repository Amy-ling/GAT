from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import LogBook
from users.models import UserProfile

# Create your views here.
##############################################
#block of system admin functions
##############################################
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import LogBook
from users.models import UserProfile
from django.contrib.auth.models import User
from .services import create_log

# Create your views here.
##############################################
#block of system admin functions
##############################################
@login_required
def sysadmin_log_list(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.is_admin:
        # Use select_related to efficiently fetch user and profile data with each log
        logs = LogBook.objects.select_related('log_user__profile').order_by('-log_date')
        context = {'logs': logs}

        if request.method == 'POST':
            user_phone = request.POST.get('user_phone')
            if user_phone:
                try:
                    # The main 'logs' query is already filtered, so we just update the context
                    up = UserProfile.objects.get(phone=user_phone)
                    filtered_logs = logs.filter(log_user__profile=up)
                    context.update({
                        'logs': filtered_logs,
                        'user_name': up.name,
                        'user_phone': user_phone,
                    })
                    create_log(request.user, f"Searched logs for user {up.name}")
                except UserProfile.DoesNotExist:
                    create_log(request.user, f"Failed to find user with phone: {user_phone}", "failure")
                    messages.warning(request, f'Input phone number: [{user_phone}] could not be found!')
                    context['logs'] = LogBook.objects.none()
            else:
                messages.warning(request, 'Please enter a phone number to search.')

        return render(request, "logs/sysadmin_log_list.html", context)
    else:
        create_log(request.user, 'admin page access denied', 'failure')
        messages.warning(request, 'You do not have permission to perform this action!')
        return redirect('users:gat_portal')

@login_required
def user_log_list(request, user_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if not user_profile.is_admin:
        create_log(request.user, 'admin page access denied', 'failure')
        messages.warning(request, 'You do not have permission to perform this action!')
        return redirect('users:gat_portal')

    target_user = get_object_or_404(User, pk=user_id)
    logs = LogBook.objects.filter(log_user=target_user).order_by('-log_date')
    
    context = {
        'logs': logs,
        'target_user_name': target_user.profile.name,
    }
    
    create_log(request.user, f"Viewed logs for user {target_user.profile.name}")
    return render(request, "logs/user_log_list.html", context)
