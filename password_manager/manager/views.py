from django.shortcuts import render
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate , login, logout
import random
from django.core.mail import send_mail
# Create your views here.
def index(request):
    if request.method == "POST":
        if "signup-form" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            password2 = request.POST.get("password2")
            if password != password2:
                msg = "Please make sure that you have entered the correct password !"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            
            if User.objects.filter(username=username).exists():
                msg = f"{username} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            
            if User.objects.filter(email=email).exists():
                msg = f"{email} already exists!"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                User.objects.create_user(username, email, password)
                new_user = authenticate(request, username=username, password=password)
                if new_user is not None:
                    login(request, new_user)
                    msg = f"{username} Thank You for Registering , You are now Login"
                    messages.success(request, msg) 
                    return HttpResponseRedirect(request.path)
        if "logout" in request.POST:      
            msg = f"{request.user}. You logged out."
            logout(request)
            messages.success(request, msg) 
            return HttpResponseRedirect(request.path)        
        
        if "login-form" in request.POST:
            username = request.POST.get("username")
            password = request.POST.get("password")
            new_login = authenticate(request, username=username, password=password)
            if new_login is None:
                msg = f"Login failed! Make sure you are using the correct account details"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)   
            else:
                code = str(random.randint(1000000, 99999))
                send_mail(
                    "P.Manager: confirm your email"
                    f"Your verfication code is {code}.",
                    settings.EMAIL_HOST_USER,
                    [new_login.email],
                    fail_silently=False,
                ) 
    return render(request, "index.html")
