from django.shortcuts import render
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate , login, logout
import random
from django.core.mail import send_mail
from cryptography.fernet import Fernet
from mechanize import Browser
import favicon
from .models import Password

br = Browser()
br.set_handle_robots(False)
fernet = Fernet(settings.KEY)

# Create your views here.

def index(request):
    if request.method == "POST":
        if "signup-form" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            password2 = request.POST.get("password2")
            if password != password2:
                msg = "Please make sure that both passwords are the same !"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)
            else:
                if username == '':
                    msg = "Please make sure that you have created a username !"
                    messages.info(request, msg)
                    return HttpResponseRedirect(request.path)            

                else:
                    if email == '':
                        msg = "Please ensure that you have entered your email !"
                        messages.info(request, msg)
                        return HttpResponseRedirect(request.path)   
            
                    else:
                        if password == '':
                            msg = "Please ensure that you have created a password !"
                            messages.info(request, msg)
                            return HttpResponseRedirect(request.path)            
            
            if User.objects.filter(username=username).exists():
                msg = f"{username} already exists!"
                messages.warning(request, msg)
                return HttpResponseRedirect(request.path)
            
            if User.objects.filter(email=email).exists():
                msg = f"{email} already exists!"
                messages.warning(request, msg)
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
            if username == '':
                msg = "Please ensure sure that you have entered your username !"
                messages.error(request, msg)
                return HttpResponseRedirect(request.path)            
            else:
                if password == '':
                    msg = "Please ensure that you have entered your password !"
                    messages.info(request, msg)
                    return HttpResponseRedirect(request.path)            
                else:
                    if new_login is None:
                        msg = f"Login failed! Make sure you are using the correct account details"
                        messages.info(request, msg)
                        return HttpResponseRedirect(request.path)
                    else:
                        code = str(random.randint(100000, 999999))
                        global global_code
                        global_code = code
                        send_mail(
                        "P.Manager: confirm email",
                        f"Your verification code is {code}.",
                        settings.EMAIL_HOST_USER,
                        [new_login.email],
                        fail_silently=False,
                    )
                    return render(request, "index.html", {
                    "code" :code,
                    "user":new_login,       
                })
            
            
    if "confirm" in request.POST:
                input_code = request.POST.get("code") 
                user = request.POST.get("user")
                if input_code != global_code:
                     msg = f"{input_code} is wrong!"
                     messages.error(request, msg)
                     return HttpResponseRedirect(request.path)
                else:
                    login(request, User.objects.get(username=user))
                    msg = f"{request.user} Welcome back"
                    messages.success(request, msg)
                    return HttpResponseRedirect(request.path)
                
    if "add-password" in request.POST:
            url = request.POST.get("url")
            email = request.POST.get("email") 
            password = request.POST.get("password") 
            encrypted_email = fernet.encrypt(email.encode())
            encrypted_password = fernet.encrypt(password.encode())
            br.open(url)
            title = br.title()
            icon = favicon.get(url)[0].url                  
            new_password = Password.objects.create(
                user=request.user,
                name=title,
                logo=icon,
                email=encrypted_email.decode(),
                password=encrypted_password.decode(),
            )    
            msg = f"{title} was successfully added."
            messages.success(request, msg)
            return HttpResponseRedirect(request.path)
        
    passwords = Password.objects.all().filter(user=request.user)
    for password in passwords:
        password.email = fernet.decrypt(password.email.encode()).decode()
        password.password = fernet.decrypt(password.password.encode()).decode()
        password.save()
        
    return render(request, "index.html" , {
        "passwords":passwords,
    })
