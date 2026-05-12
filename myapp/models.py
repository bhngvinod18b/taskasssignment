from django.db import models
from django.contrib.auth.models import User


# ---------------- PROFILE ----------------
class Myprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    employe_id = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


# ---------------- TASK ----------------
class Task_assign(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name="manager_tasks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="employee_tasks")
    task = models.CharField(max_length=100)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('todo', 'Todo'),
        ('completed', 'Completed'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.manager.username} → {self.user.username}"


# ---------------- NOTIFICATION ----------------
class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages", blank=True, null=True)
    reciver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} → {self.reciver.username}"
    
class Manager(models.Model):
    manager_name = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user}"