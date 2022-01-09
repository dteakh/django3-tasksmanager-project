from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from todoapp.forms import TasksForm
from .models import Tasks


@login_required
def currenttasks(request):
    tasks = Tasks.objects.filter(user=request.user, completed__isnull=True)
    return render(request, 'todoapp/currenttasks.html', {'tasks': tasks})


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todoapp/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttasks')
            except IntegrityError:
                return render(request, 'todoapp/signupuser.html', {'form': UserCreationForm(),
                                                                   'error': 'This username is already taken'})
        else:
            return render(request, 'todoapp/signupuser.html', {'form': UserCreationForm(),
                                                               'error': 'Passwords didn\'t match. Try again'})


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todoapp/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todoapp/loginuser.html', {'form': AuthenticationForm(),
                                                              'error': 'Username or Password is wrong'})
        else:
            login(request, user)
            return redirect('currenttasks')


def home(request):
    return render(request, 'todoapp/base.html')


@login_required
def newtask(request):
    if request.method == 'GET':
        return render(request, 'todoapp/newtask.html', {'form': TasksForm})
    else:
        try:
            form = TasksForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('currenttasks')
        except ValueError:
            return render(request, 'todoapp/newtask.html', {'form': TasksForm, 'error': 'Something wrong was passed.'
                                                                                        ' Please, try again.'})


@login_required
def taskinfo(request, task_id):
    task = get_object_or_404(Tasks, pk=task_id, user=request.user)
    form = TasksForm(instance=task)
    if request.method == 'GET':
        return render(request, 'todoapp/taskinfo.html', {'task': task, 'form': form})
    else:
        try:
            form = TasksForm(request.POST, instance=task)
            form.save()
            return redirect('currenttasks')
        except ValueError:
            render(request, 'todoapp/taskinfo.html', {'task': task, 'form': form, 'error': 'Bad data was passed. Please'
                                                                                           'try again.'})


@login_required
def taskcompleted(request, task_id):
    task = get_object_or_404(Tasks, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.completed = timezone.now()
        task.save()
        return redirect('currenttasks')


@login_required
def taskdelete(request, task_id):
    task = get_object_or_404(Tasks, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('currenttasks')


@login_required
def completed(request):
    tasks = Tasks.objects.filter(user=request.user, completed__isnull=False).order_by('-completed')
    return render(request, 'todoapp/completed.html', {'tasks': tasks})
