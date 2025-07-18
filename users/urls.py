from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import UserLoginForm

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register_view'),

    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        authentication_form=UserLoginForm # Use our custom form
    ), name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile'),

    # Password Change Paths
    path('password-change/', views.CustomPasswordChangeView.as_view(
        template_name='users/password_change.html',
        success_url=reverse_lazy('users:password_change_done') # URL to redirect to on success
    ), name='password_change'),

    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='users/password_change_done.html'
    ), name='password_change_done'),

    path('gat_portal/', views.gat_portal, name='gat_portal'),
    path('sysadmin/', views.sysadmin_main, name='sysadmin_main'),
    path('sysadmin/reset_pwd/', views.sysadmin_reset_pwd, name='systemadmin_reset_pwd'),
    path('admin_profile/', views.admin_profile_view, name='admin_profile'),
    path('admin/password-change/', views.AdminPasswordChangeView.as_view(), name='admin_password_change'),
    path('admin/password-change/done/', views.AdminPasswordChangeDoneView.as_view(), name='admin_password_change_done'),
    path('admin/search/', views.admin_search, name='admin_search'),
]
