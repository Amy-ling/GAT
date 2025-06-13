from django.shortcuts import render, redirect
from django.contrib import messages
# Import the decorator
from django.contrib.auth.decorators import login_required
# Import your forms
from .forms import UserRegisterForm, UserProfileUpdateForm
from django.contrib.auth.models import User
from .models import LogBook
from django.http import HttpResponse

# Create your views here.
def logbook_save(uid, action, result):
    LogBook.objects.create(log_action=action.upper(), log_result=result.upper(), log_user_id=uid)

def gat_index(request):
    return render(request, "gat_app/index.html")

@login_required
def gat_user_index(request):
    return render(request, "gat_app/user_main.html")

@login_required
def systemadmin_index(request):
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