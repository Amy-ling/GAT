from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'items'  # Add this line

urlpatterns = [
    path('give/', views.give_item_view, name='give_item'),
    path('<int:item_id>/take/', views.take_item_view, name='take_item'),
    # path('<int:pk>/confirm_take/', views.confirm_take_item_view, name='confirm_take_item'),
    path('<int:item_id>/edit/', views.edit_item_view, name='edit_item'),
    path('<int:item_id>/delete/', views.delete_item_view, name='delete_item'),
    path('history/', views.my_history_view, name='my_history'),
    path('main/', views.user_main_view, name='user_main'),

]
