from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from .models import Myprofile, Task_assign, Notification, Manager


# ---------------- HOME ----------------
from .models import Task_assign, Notification

@login_required
def home(request):
    if request.user.is_staff:
        return redirect('manager_profile')

    task = Task_assign.objects.filter(user=request.user).order_by('-id')

    notifications = Notification.objects.filter(
        reciver=request.user
    ).order_by('-id')[:5]   # latest 10

    return render(request, 'myapp/home.html', {
        'task': task,
        'notifications': notifications
    })

# ---------------- MANAGER PROFILE ----------------
@login_required
def manager_profile(request):
    if not request.user.is_staff:
        return redirect('home')

    manager = Manager.objects.filter(manager_name=request.user).first()

    if request.method == 'POST':
        phone = request.POST.get('phone')

        if phone:
            Manager.objects.update_or_create(
                manager_name=request.user,
                defaults={
                    'phone': phone
                }
            )

            messages.success(request, "Manager saved successfully")

        return redirect('manager_profile')  # better than home

    return render(request, 'myapp/manager.html', {
        'manager': manager
    })
# ---------------- EMPLOYEE PROFILE ----------------
@login_required
def myprofile(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        employe_id = request.POST.get('employe_id')

        if phone and department and employe_id:
            Myprofile.objects.update_or_create(
                user=request.user,
                defaults={
                    'phone': phone,
                    'department': department,
                    'employe_id': employe_id
                }
            )

    return render(request, 'myapp/employe.html')


# ---------------- GIVE TASK ----------------

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Task_assign
from .tasks import create_task_notification


@login_required
def give_task(request):
    if not request.user.is_staff:
        return redirect('home')

    users = User.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user')
        task = request.POST.get('task')
        status = request.POST.get('status')

        if user_id and task and status:
            assigned_user = User.objects.get(id=user_id)

            # 1. SAVE TASK
            Task_assign.objects.create(
                manager=request.user,
                user=assigned_user,
                task=task,
                status=status
            )

            # 2. SEND CELERY TASK (IMPORTANT)
            from .tasks import create_task_notification

            create_task_notification.delay(
                assigned_user.id,
                request.user.id,
                task
            )

        return redirect('home')

    return render(request, 'myapp/task.html', {
        'users': users
    })

@login_required
def delete_task(request, id):
    if not request.user.is_staff:
        return redirect('home')

    task = get_object_or_404(Task_assign, id=id)

    if task.status != "completed":
        return redirect('home')

    task.delete()
    return redirect('manager_dashboard')
@login_required
def edit_task(request, id):
    task = get_object_or_404(Task_assign, id=id, user=request.user)
    if request.method == 'POST':
        task.status = request.POST.get('status')
        task.save() 
    return redirect('home')
        


# ---------------- MANAGER DASHBOARD ----------------
from django.core.paginator import Paginator

@login_required
def manager_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

    manager = request.user

    all_tasks_qs = Task_assign.objects.filter(manager=request.user).order_by('-id')

    pending = Task_assign.objects.filter(manager=request.user, status='pending')
    todo = Task_assign.objects.filter(manager=request.user, status='todo')
    completed = Task_assign.objects.filter(manager=request.user, status='completed')

    # ✅ Pagination only for table
    paginator = Paginator(all_tasks_qs, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/manager_dashboard.html', {
        'all_task': page_obj,   # table uses this
        'page_obj': page_obj,   # pagination controls
        'pending': pending,
        'todo_task': todo,
        'completed_task': completed,
        'manager': manager
    })

# ---------------- SEND MESSAGE (MANAGER → EMPLOYEE) ----------------
@login_required
def sender_message(request, id):
    profile = get_object_or_404(Myprofile, user_id=id)
    reciver = profile.user

    if request.method == 'POST':
        content = request.POST.get('content')

        if content:
            Notification.objects.create(
                sender=request.user,
                reciver=reciver,
                content=content
            )
            return redirect('home')

    return render(request, 'myapp/sender_manager.html', {'profile': profile})


# ---------------- SEND MESSAGE (EMPLOYEE → MANAGER) ----------------
@login_required
def send_employee(request, id):
    receiver = get_object_or_404(Manager, id=id)

    if request.method == 'POST':
        content = request.POST.get('content')

        if content:
            Notification.objects.create(
                sender=request.user,
                reciver=receiver,
                content=content
            )
            return redirect('home')

    return render(request, 'myapp/sender_employe.html')


# ---------------- INBOX ----------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Notification


# 🔹 Inbox = list of users (like WhatsApp home)
@login_required
def inbox(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'myapp/inbox_list.html', {'users': users})
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        reciver=request.user
    ).order_by('-created_at')

    return render(request, 'myapp/notification.html', {
        'notifications': notifications
    })


# 🔹 Chat with selected user
@login_required
def ct(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # SEND MESSAGE
    if request.method == 'POST':
        content = request.POST.get('content')

        if content:
            Notification.objects.create(
                sender=request.user,
                reciver=other_user,   # your field name
                content=content
            )
            return redirect('chat', user_id=other_user.id)

    # GET CHAT
    messages = Notification.objects.filter(
        Q(sender=request.user, reciver=other_user) |
        Q(sender=other_user, reciver=request.user)
    ).order_by('created_at')

    return render(request, 'myapp/chat.html', {
        'messages': messages,
        'other_user': other_user
    })

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
@login_required
def chat(request, user_id):

    other_user = get_object_or_404(User, id=user_id)

    # SEND MESSAGE
    if request.method == 'POST':

        content = request.POST.get('content')

        if content:

            # SAVE MESSAGE
            Notification.objects.create(
                sender=request.user,
                reciver=other_user,
                content=content
            )

            # REALTIME NOTIFICATION
            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                f"user_{other_user.id}",
                {
                    "type": "send_notification",
                    "sender": request.user.username,
                    "message": content,
                }
            )

            return redirect('chat', user_id=other_user.id)

    # GET CHAT
    messages = Notification.objects.filter(
        Q(sender=request.user, reciver=other_user) |
        Q(sender=other_user, reciver=request.user)
    ).order_by('created_at')

    return render(request, 'myapp/chat.html', {
        'messages': messages,
        'other_user': other_user
    })
# 
# ---------------- AUTH ----------------
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            return redirect('home')

        messages.error(request, "Invalid credentials")

    return render(request, 'myapp/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

from myproject.celery_app import app
def register(request):
    from django.contrib.auth.forms import UserCreationForm

    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')

    return render(request, 'myapp/register.html', {'form': form})

from rest_framework import viewsets
from .serializers import ManagerSerializer, MyprofileSerializer, Task_assignSerializer
from .serializers import NotificationSerializer

class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    lookup_field = 'phone'
    search_field = ['phone', 'manager_name']
class MyprofileViewSet(viewsets.ModelViewSet):
    queryset = Myprofile.objects.all()
    serializer_class = MyprofileSerializer
    lookup_field = 'phone'
    search_field = ['phone', 'department', 'employe_id']

class Task_assignViewSet(viewsets.ModelViewSet):
    queryset = Task_assign.objects.all()
    serializer_class = Task_assignSerializer
    lookup_field = 'task'
    search_field = ['task', 'user', 'manager', 'status', ]
    
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    lookup_field = 'reciver'
    search_field = ['sender', 'reciver', 'content']


