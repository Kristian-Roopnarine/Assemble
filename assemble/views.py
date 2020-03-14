from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Project,ProjectComponent,FriendRequest,Profile
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
# django form for creating a user 
from .forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
from django.db.models import Q
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
        messages.success(self.request,f"Created {form.instance.name}")
        return redirect('project-list')
        
# view to create project components
class ProjectComponentCreate(LoginRequiredMixin,CreateView):
    model = ProjectComponent
    fields = ['name','description']
    
    def form_valid(self,form):
        project = Project.objects.get(slug=self.kwargs['project_slug'])
        form.instance.project = project
        super().form_valid(form)
        messages.success(self.request,f"Added '{form.instance.name}' to {project.name}")

        # this takes the models get_absolute_url and redirects to the URL
        return redirect(project)
    
    def get_context_data(self,**kwargs):
        context= super().get_context_data(**kwargs)
        project = Project.objects.get(slug=self.kwargs['project_slug'])
        context['project'] = project
        return context

class ProjectTaskCreate(LoginRequiredMixin,CreateView):
    model = ProjectComponent
    fields = ['name']
    template_name = "assemble/componenttask_form.html"

    def form_valid(self,form):
        component = ProjectComponent.objects.get(slug=self.kwargs['project_component_slug'])
        form.instance.project = component.project
        form.instance.task = component
        super().form_valid(form)
        messages.success(self.request,f"Added '{form.instance.name}' to '{form.instance.task}'")
        return redirect(component.project)
    
    def get_context_data(self,**kwargs):
        context= super().get_context_data(**kwargs)
        component = ProjectComponent.objects.get(slug=self.kwargs['project_component_slug'])
        context['component'] = component
        return context

@login_required
# view components of a project
def project_detail_view(request,project_slug):
    project = Project.objects.filter(user=request.user).get(slug=project_slug)
    project_components = ProjectComponent.objects.filter(project__name=project).filter(task=None)
    context = {
        'project':project,
        'project_components':project_components,
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

def finish_task_detail(request,id):
    task = get_object_or_404(ProjectComponent,id=id)
    before=task.completed
    task.completed= not before
    task.save()
    return redirect(task.project)

def delete_task(request,id):
    task = get_object_or_404(ProjectComponent,id=id)
    task.delete()
    return redirect(task.project)

@login_required
def profile(request):
    current_projects = Project.objects.filter(user=request.user)
    profile = Profile.objects.get(user__username=request.user)
    friend_requests = FriendRequest.objects.filter(Q(to_user__username=request.user.username) | Q(from_user__username=request.user.username))
    print(friend_requests)
    context={
        'current_projects':current_projects,
        'profile':profile,
        'friend_requests':friend_requests,
        
    }
    return render(request,'assemble/profile.html',context)

def profile_view(request,slug):
    p = Profile.objects.filter(slug=slug).first()
    u = p.user
    context={
        'u':u
    }
    return render(request,'assemble/profile_view.html',context)


def search_user(request):
    try:
        filtered_user = Profile.objects.get(user__username=request.POST['username'])
        if request.user.username == filtered_user.user.username:
            return redirect('profile')
    except ObjectDoesNotExist:
        filtered_user = 0
    context={
        'filtered_user':filtered_user,
        'username':request.POST['username']
    }
    return render(request,'assemble/search_user.html',context)

@login_required
def send_friend_request(request,sent_to):
    user = get_object_or_404(Profile,user__username=sent_to)
    frequest = FriendRequest.objects.get_or_create(
        to_user=user.user,
        from_user=request.user,
    )
    return redirect('profile-view',slug=user.slug)


    # create a friend request object
    # link the to_user and from_user
    # to_user = visiting profile
    # from_user = request.user
    