from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Profiles
    path('manager-profile/', views.manager_profile, name='manager_profile'),
    path('employee-profile/', views.myprofile, name='myprofile'),

    # Task
    path('give-task/', views.give_task, name='give_task'),

    # Manager Dashboard
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),

    # Messaging
    path('send-message/<int:id>/', views.sender_message, name='sender_message'),
    path('send-employee/<int:id>/', views.send_employee, name='send_employee'),

    # Inbox
    path('inbox/', views.inbox, name='inbox'),                 # list
    path('chat/<int:user_id>/', views.chat, name='chat'),
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('edit-task/<int:id>/', views.edit_task, name='edit_task'),

]