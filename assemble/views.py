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
from django.contrib.auth.models import User
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
    fields = ['name','description','user']
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

@login_required
def component_task_detail(request,project_component_slug,component_task_slug):
    return render(request,'assemble/task_detail.html')

@login_required
def finish_task_detail(request,id):
    task = get_object_or_404(ProjectComponent,id=id)
    before=task.completed
    task.completed= not before
    task.save()
    return redirect(task.project)

@login_required
def delete_task(request,id):
    task = get_object_or_404(ProjectComponent,id=id)
    task.delete()
    return redirect(task.project)

@login_required
def profile(request):
    current_projects = Project.objects.filter(user=request.user)
    profile = Profile.objects.get(user__username=request.user)
    #queryset containing all friend request objects
    friend_requests = FriendRequest.objects.filter(Q(to_user__username=request.user.username) | Q(from_user__username=request.user.username))
    context={
        'current_projects':current_projects,
        'profile':profile,
        'friend_requests':friend_requests,
        
    }
    return render(request,'assemble/profile.html',context)

@login_required
def profile_view(request,slug):
    p = Profile.objects.filter(slug=slug).first()
    is_me = Profile.objects.get(user__username=request.user)
    search_query = p.user
    try:
        frequest = FriendRequest.objects.get(
            to_user=search_query,
            from_user=request.user,
        )
        sent_request = True
    except ObjectDoesNotExist:
        sent_request = False

    try:
        Profile.objects.filter(slug=slug).get(friends=is_me)
        already_friends=True
    except ObjectDoesNotExist:
        already_friends=False
    context={
        'search_query':search_query,
        'sent_request':sent_request,
        'already_friends':already_friends
    }
    return render(request,'assemble/profile_view.html',context)


@login_required
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
    # create a friend request object
    # link the to_user and from_user
    # to_user = visiting profile
    # from_user = request.user
    user = get_object_or_404(Profile,user__username=sent_to)
    frequest,created = FriendRequest.objects.get_or_create(
        to_user=user.user,
        from_user=request.user,
    )
    return redirect('profile-view',slug=user.slug)

@login_required
def accept_friend_request(request,from_user):
    # get the from user in the db
    user = get_object_or_404(Profile,user__username=from_user)

    #get me from the db
    is_me = Profile.objects.get(user__username=request.user.username)
    
    # add from_user to your friend list
    is_me.friends.add(user)
    # add your profile to their friend list
    user.friends.add(is_me)
    frequest = FriendRequest.objects.get(from_user=user.user,to_user=is_me.user)

    # save
    is_me.save()
    user.save()
    # if succesful redirect to delete request
    return redirect('delete-friend-request',frequest.id)

@login_required
def delete_friend_request(request,id):
    frequest= FriendRequest.objects.get(id=id)
    frequest.delete()
    # delete
    # redirect to user profile
    return redirect('profile')