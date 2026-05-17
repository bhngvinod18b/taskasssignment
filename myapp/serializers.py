from rest_framework import serializers
from .models import Manager, Myprofile, Task_assign, Notification

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = '__all__'
        
class MyprofileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Myprofile
        fields = '__all__'
        
class Task_assignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task_assign
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        
    
