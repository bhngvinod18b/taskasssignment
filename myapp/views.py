from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from .models import Myprofile, Task_assign, Notification, Manager


# ---------------- HOME ----------------
@login_required
def home(request):
    if request.user.is_staff:
        return redirect('manager_profile')
    task = Task_assign.objects.filter(user=request.user)
    return render(request, 'myapp/home.html', {'task': task})


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

@login_required
def give_task(request):
    if not request.user.is_staff:
        return redirect('home')  # block non-managers

    manager = request.user
    users = User.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user')
        task = request.POST.get('task')
        status = request.POST.get('status')

        if user_id and task and status:
            Task_assign.objects.create(
                manager=manager,
                user_id=user_id,
                task=task,
                status=status
            )
            return redirect('home')

    return render(request, 'myapp/task.html', {
        'users': users,
        'manager': manager
    })
    
@login_required
def edit_task(request, id):
    task = get_object_or_404(Task_assign, id=id, user=request.user)
    if request.method == 'POST':
        task.status = request.POST.get('status')
        task.save() 
    return redirect('home')
        


# ---------------- MANAGER DASHBOARD ----------------
@login_required
def manager_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    manager = request.user
    all_task = Task_assign.objects.filter(manager=request.user)
    pending = Task_assign.objects.filter(manager=request.user, status='pending')
    todo = Task_assign.objects.filter(manager=request.user, status='todo')
    completed = Task_assign.objects.filter(manager=request.user, status='completed')

    return render(request, 'myapp/manager_dashboard.html', {
        'all_task': all_task,
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


def register(request):
    from django.contrib.auth.forms import UserCreationForm

    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')

    return render(request, 'myapp/register.html', {'form': form})