from django.shortcuts import render,redirect
from django.views.generic import ListView
from .models import Project

# django form for creating a user 
from .forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
# Create your views here.

# home
@login_required
def index(request):
    return render(request,'assemble/index.html')

# sign up view
def sign_up(request):
    context = {}
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user= form.save()
            login(request,user)
            redirect('home')
    context['form'] = form

    return render(request,'registration/sign_up.html',context)

# List view of all the projects for a user
class ProjectList(ListView):
    model = Project