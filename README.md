# 📋 Django Employee Task Management System

A full-stack Employee Task Management System built using Django.  
This project allows managers to assign tasks, employees to update task status, real-time messaging, notifications, and REST APIs.
this is task management it is about manager assign task to employe employr work on it and give updates with live notifications whatsapp like chat and manager
can deleted completed task manager dashboard shows all task list with stetus like pending todo completed ect it hase employe dashboard aslo with task given ect 
can make status change pending todo completed ect and celery reddies work as baground task when manager assign a task employe get live notifications on home page.

---
# live https://taskasssignment.onrender.com
# 🌐 Features

## 👨‍💼 Manager Features
- Manager Profile Management
- Assign Tasks to Employees
- Track Task Status
- View Pending / Todo / Completed Tasks
- Delete Completed Tasks
- Send Messages to Employees
- Dashboard with Pagination

---

## 👨‍💻 Employee Features
- Employee Profile Management
- View Assigned Tasks
- Update Task Status
- Receive Notifications
- Real-time Chat with Manager
- Inbox & Messaging System

---

## 💬 Chat & Notifications
- Real-time Notifications using Django Channels
- User-to-User Chat System
- Inbox Messaging
- Latest Notifications Panel

---

## 🔐 Authentication
- User Registration
- Login & Logout
- Role-based Access Control
- Protected Routes using `login_required`

---

## ⚡ Advanced Features
- Celery Background Tasks
- Real-time WebSocket Notifications
- REST API using Django REST Framework
- Pagination for Large Task Lists
- Search & Filtering

---

# 🛠 Technologies Used

- Python
- Django
- Django REST Framework
- Django Channels
- Celery
- SQLite
- HTML
- CSS
- Bootstrap
- JavaScript
- Git & GitHub

---

# 📂 Project Structure

```bash
myproject/
│
├── myapp/
│   ├── templates/
│   ├── serializers.py
│   ├── tasks.py
│   ├── views.py
│   ├── models.py
│   └── urls.py
│
├── myproject/
│
├── manage.py
├── requirements.txt
└── Procfile
