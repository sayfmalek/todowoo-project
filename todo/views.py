from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        return render(request, 'todo/loggedhome.html')
    else:
        return render(request, 'todo/home.html')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    
    else:
        if request.POST['password1'] == request.POST['password2'] and request.POST['password1'] != '':
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                #to login the user
                login(request, user)
                #after login redirect user to his current todo page
                return redirect('currenttodo')

            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Username has already been taken. Try another.'})

            except ValueError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Type in Username and Password'})
        
        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Password did not match'}) 


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username and assword did not match'}) 
        else:
            login(request, user)
            #after login redirect user to his current todo page
            return redirect('currenttodo')
        

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')



#Todo views
@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})

    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodo')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': TodoForm(), 'error': 'Bad data is passed in. Try again.'})


@login_required
def currenttodo(request):
    todos = Todo.objects.filter(user=request.user, datecomplete__isnull=True).order_by('-created')
    return render(request, 'todo/currenttodo.html', {'todos': todos})


@login_required
def completedtodo(request):
    todos = Todo.objects.filter(user=request.user, datecomplete__isnull=False).order_by('-datecomplete')
    return render(request, 'todo/completedtodo.html', {'todos': todos})


@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})

    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodo')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'error': 'Bad info is passed in. Try again.'})


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecomplete = timezone.now()
        todo.save()
        return redirect('currenttodo')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodo')
