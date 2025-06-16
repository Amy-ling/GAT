# gat_app/urls.py

from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import UserLoginForm
urlpatterns = [
    path('', views.gat_index, name="gat_index"),
    path('register/', views.register_view, name="register_view"),

    path('login/', auth_views.LoginView.as_view(
        template_name='gat_app/login.html',
        authentication_form=UserLoginForm # Use our custom form
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        template_name='gat_app/logout.html' # Specify template for the logout confirmation page
    ), name='logout'),

    path('profile/', views.profile_view, name='profile'),

    # Password Change Paths
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='gat_app/password_change.html',
        success_url=reverse_lazy('password_change_done') # URL to redirect to on success
    ), name='password_change'),

    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='gat_app/password_change_done.html'
    ), name='password_change_done'),

    path('gat_portal/', views.gat_portal, name="gat_portal"),
    path('syslog_list/', views.sysadmin_log_list, name="sysadmin_log_list"),
    path('syslog_delete/<pk>/', views.systemadmin_log_delete, name="systemadmin_log_delete"),
    path('sys_reset_pwd/', views.systemadmin_reset_pwd, name="systemadmin_reset_pwd"),
    path('reset_pwd/', views.user_reset_pwd, name="user_reset_pwd"),
    path('user/reset_pwd/', views.user_reset_pwd, name="user_reset_pwd"),
    path('item/give/', views.give_item_view, name='give_item'),
    path('item/take/', views.take_item_view, name='take_item'),
    path('user/history/', views.user_history_view, name='user_history'),
    path('item/<int:pk>/edit/', views.edit_item_view, name='edit_item'),
    path('item/<int:pk>/delete/', views.delete_item_view, name='delete_item'),
    path('item/take/', views.take_item_view, name='take_item'),
    path('user/history/', views.user_history_view, name='user_history'),
]