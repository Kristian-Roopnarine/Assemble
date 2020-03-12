from django.shortcuts import render,redirect
from django.views.generic import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Project,ProjectComponent

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
            return redirect('home')
    context['form'] = form

    return render(request,'registration/sign_up.html',context)

# List view of all the projects for a user
class ProjectList(LoginRequiredMixin,ListView):
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

# view to create project components
class ProjectComponentCreate(LoginRequiredMixin,CreateView):
    model = ProjectComponent
    fields = ['name','description']
    
    def form_valid(self,form):
        project = Project.objects.get(slug=self.kwargs['project_slug'])
        form.instance.project = project
        super().form_valid(form)

        # this takes the models get_absolute_url and redirects to the URL
        return redirect(project)

class ProjectTaskCreate(LoginRequiredMixin,CreateView):
    model = ProjectComponent
    fields = ['name','description']

    def form_valid(self,form):
        component = ProjectComponent.objects.get(slug=self.kwargs['project_component_slug'])
        form.instance.project = component.project
        form.instance.task = component
        super().form_valid(form)
        return redirect(component)

@login_required

# view components of a project
def project_detail_view(request,project_slug):
    project = Project.objects.filter(user=request.user).get(slug=project_slug)
    project_components = ProjectComponent.objects.filter(project__name=project).filter(task=None)
    context = {
        'project':project,
        'project_components':project_components
    }
    return render(request,'assemble/project_detail.html',context)

@login_required
# view tasks of a component
def project_component_detail_view(request,project_component_slug):
    component = ProjectComponent.objects.get(slug=project_component_slug)
    component_tasks = component.component.all()
    context = {
        'component_tasks':component_tasks,
        'component':component,
    }
    return render(request,'assemble/project_component.html',context)

def component_task_detail(request,project_component_slug,component_task_slug):
    return render(request,'assemble/task_detail.html')