from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib.auth import login as dj_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.conf import settings

from .forms import LoginUserForm, UserPasswordChangeForm, RegisterForm
from .models import User

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import uuid4
import smtplib
from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def media(file_path):
    return f"{settings.MEDIA_URL}{file_path}"

def ulogin(request):
    validAuth = ""
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = LoginUserForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                user = User.objects.filter(username=username).first()
                if user and user.check_password(password):
                    dj_login(request, user)
                    return HttpResponseRedirect(reverse('users:profile'))
                else:
                    validAuth = "Неверные логин или пароль"
        else:
            form = LoginUserForm()
        context = {"form": form, "errors": validAuth}
        return render(request, "users/login.html", context=context)
    else:
        return HttpResponseRedirect(reverse('users:profile'))

def register(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = RegisterForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"]
                email = form.cleaned_data["email"]
                password = form.cleaned_data["password"]
                user = User.objects.create(username=username, email=email, confirm_key=str(uuid4()))
                user.set_password(password)
                user.save()
                context = {"user": user, "url": request.get_host()}
                return HttpResponseRedirect(reverse("users:login"))
        else:
            form = RegisterForm()
        context = {"form": form}
        return render(request, "users/register.html", context=context)
    else:
        return HttpResponseRedirect(reverse('users:profile'))
    
def ulogout(request):
    logout(request)
    return HttpResponseRedirect(reverse('users:login'))


@login_required(login_url="users:login")
def profile(request):
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        if photo:
            request.user.photo = photo
            request.user.save()
    created_quizes = eval(str(request.user.created_quizes))
    context = {'user': request.user, 'created_quizes': created_quizes}
    return render(request, 'users/profile.html', context=context)

def user_page(request, user_id):
    print(user_id)
    user = get_object_or_404(User, id=user_id)
    print(user)
    created_quizes = eval(str(user.created_quizes))
    context = {'user': request.user, "user_page": user, 'created_quizes': created_quizes}
    return render(request, 'users/user.html', context=context)

class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:profile")
    template_name = "users/password_change_form.html"
    # <!-- <a href="{% url 'users:password_change' %}" style="font-family: Comic Sans MS; !important" class="btn btn-dark btn-sm btn-block">Сменить пароль</a> -->
