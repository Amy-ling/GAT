from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'logs'

urlpatterns = [
    path('sysadmin/log_list/', views.sysadmin_log_list, name='sysadmin_log_list'),
    path('sysadmin/log_list/<int:user_id>/', views.user_log_list, name='user_log_list'),
]
