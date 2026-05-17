from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ManagerViewSet
from .views import MyprofileViewSet
from .views import Task_assignViewSet
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r'manager', ManagerViewSet, basename='manager')
router.register(r'my-profile', MyprofileViewSet, basename='my-profile')
router.register(r'noti-fication', NotificationViewSet, basename='notifi-cation')
router.register(r'task', Task_assignViewSet, basename='task')
urlpatterns = [
    # Django normal routes
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    path('myprofile/', views.myprofile, name='myprofile'),
    path('manager-profile/', views.manager_profile, name='manager_profile'),

    path('give-task/', views.give_task, name='give_task'),
    path('edit-task/<int:id>/', views.edit_task, name='edit_task'),
    path('delete-task/<int:id>/', views.delete_task, name='delete_task'),

    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),

    path('send-message/<int:id>/', views.sender_message, name='sender_message'),
    path('send-employee/<int:id>/', views.send_employee, name='send_employee'),

    path('notifications/', views.notification_list, name='notifications'),

    path('inbox/', views.inbox, name='inbox'),
    path('chat/<int:user_id>/', views.chat, name='chat'),

    path('ct/<int:user_id>/', views.ct, name='ct'),

    # DRF routes
    path('', include(router.urls)),
]