from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm


def register_user(request):
    context = {'register_user': RegisterForm()}
    if request.POST:
        form = RegisterForm(request.POST)
    else:
        return render(request, template_name='register/register.html', context=context)
    if form.is_valid():
        form.save()
        login(request, form.Meta.model)
        messages.success(request, 'Account created successfully')
        return redirect('home')
    else:
        messages.error(request, "Invalid input")
        return render(request, template_name='register/register.html', context=context)


def login_user(request):
    context = {'login_user': AuthenticationForm()}
    if request.POST:
        pass
    else:
        return render(request, template_name='register/login.html', context=context)
    form = AuthenticationForm(data=request.POST)

    if form.is_valid():
        form.clean()
    else:
        messages.error(request, 'Invalid input')
        return render(request, template_name='register/login.html', context=context)

    user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
    if user is not None:
        login(request, user)
        return redirect('home')
    else:
        messages.error(request, 'Invalid username/password')
        return render(request, template_name='register/login.html', context=context)


def logout_user(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('home')
