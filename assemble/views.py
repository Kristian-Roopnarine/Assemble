from django.shortcuts import render,redirect
from django.views.generic import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
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
    
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

# view to create more projects
class ProjectCreate(LoginRequiredMixin,CreateView):
    model = Project
    fields = ['name','description']
    success_url = reverse_lazy('project-list')

    def form_valid(self,form):
        super().form_valid(form)
        form.instance.user.add(self.request.user)
        # needs to return a HttpResponse Object
        # before it returned super().form_valid(form)
        # however when using a m2m relationship, the object needs to be saved FIRST, then relationships can be made.
        return redirect('project-list')