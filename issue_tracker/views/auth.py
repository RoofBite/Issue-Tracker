from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from lazysignup.utils import is_lazy_user
from lazysignup.decorators import allow_lazy_user
from ..forms import CreateUserForm



@allow_lazy_user
def sign_in(request):
    if request.user.is_authenticated and not is_lazy_user(request.user):
        return redirect("issue_tracker:main")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("issue_tracker:main")
        else:
            messages.info(request, "Wrong password or username")
            return redirect(request.path)
    else:
        return render(request, "issue_tracker/sign_in.html")

@allow_lazy_user
def sign_up(request):
    if request.user.is_authenticated and not is_lazy_user(request.user):
        return redirect("issue_tracker:main")

    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("issue_tracker:sign-in")

    context = {"form": form}
    return render(request, "issue_tracker/sign_up.html", context)


@login_required
def logout_page(request):
    logout(request)
    return redirect("issue_tracker:sign-in")
