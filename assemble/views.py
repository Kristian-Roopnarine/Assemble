from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Project,ProjectComponent,FriendRequest,Profile
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

# django form for creating a user 
from .forms import UserCreationForm,ProjectCreateForm,ProjectEditForm,ComponentEditForm,UserFeedbackCreateForm
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


def log_out(request):
    context = {}
    form = UserFeedbackCreateForm()
    context['form']= form
    logout(request)
    if request.method == 'POST':
        form = UserFeedbackCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Thank you for your feedback!')
            return redirect('home')
    return render(request,'registration/logged_out.html',context)

# List view of all the projects for a user
class ProjectList(LoginRequiredMixin,ListView):
    model = Project
    
    # i think I can turn this into one line
    # I'm using the request data to pull my user instance from it
    # getting the profile with that user instance
    # getting the projects associated with that profile
    def get_queryset(self):
        is_me = Profile.objects.get(user=self.request.user)
        return Project.objects.filter(user=is_me)

# view to create more projects
class ProjectCreate(LoginRequiredMixin,CreateView):
    form_class = ProjectCreateForm
    template_name = "assemble/project_form.html"
    success_url = reverse_lazy('project-list')

    # addings key word arguments to this class
    # in this case we're adding the user
    def get_form_kwargs(self):
        kwargs = super(ProjectCreate,self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self,form):
        is_me = Profile.objects.get(user=self.request.user)
        form.instance.owner=is_me
        super().form_valid(form)
        form.instance.user.add(is_me)
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

    # get my profile
    is_me = Profile.objects.get(user=request.user)

    # get the project with the project slug passed in from the button
    # maybe I can use project id instead?
    project = Project.objects.filter(user=is_me).get(slug=project_slug)

    # get the components of the project
    # task=None ensures that the component is not a task!
    project_components = ProjectComponent.objects.filter(project__name=project).filter(task=None)
    context = {
        'project':project,
        'project_components':project_components,
    }
    return render(request,'assemble/project_detail.html',context)


@login_required
# view tasks of a component
# do I even use this
# reconsider
def project_component_detail_view(request,project_component_slug):
    component = ProjectComponent.objects.get(slug=project_component_slug)
    component_tasks = component.component.all()
    context = {
        'component_tasks':component_tasks,
        'component':component,
    }
    return render(request,'assemble/project_component.html',context)
"""
@login_required
#reconsider using this
def component_task_detail(request,project_component_slug,component_task_slug):
    return render(request,'assemble/task_detail.html')
"""

@login_required
def finish_task_detail(request,id):
    task = get_object_or_404(ProjectComponent,id=id)
    before=task.completed
    task.completed= not before
    task.save()
    messages.success(request,f"The task '{task}' completed status was changed to {task.completed}.")
    return redirect(task.project)

@login_required
def delete_task(request,id):
    task = get_object_or_404(ProjectComponent,id=id)
    messages.success(request,f"Successfully deleted {task}")
    task.delete()
    return redirect(task.project)

@login_required
def profile(request):
    is_me = Profile.objects.get(user=request.user)
    # I think I can query this from my profile instance
    current_projects = Project.objects.filter(user=is_me)

    # I'm querying this twice
    # TODO: remove this line
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
    # using slugs because they are passed in, maybe use id instead?

    p = Profile.objects.filter(slug=slug).first()
    is_me = Profile.objects.get(user__username=request.user)
    search_query = p.user
    # need to check if I already sent a friend request to this user
    # query all the requests from_user== me then filter by to_user
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
    messages.success(request,f"Friend request succesfully sent to {user}")
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
    messages.success(request,f"You and {user} are now friends! You can work on projects together.")
    return redirect('delete-friend-request',frequest.id)

@login_required
def delete_friend_request(request,id):
    frequest= FriendRequest.objects.get(id=id)
    frequest.delete()
    # delete
    # redirect to user profile
    return redirect('profile')


@login_required
# only owner can delete this
# use delete view?
def delete_project(request,id):
    project = Project.objects.get(id=id)
    context = {
        'project':project
    }
    if request.method == "GET":
        return render(request,'assemble/delete.html',context)
    elif request.method == 'POST':
        project.delete()
        return redirect('project-list')
"""
TODO: find out why this wasn't working
Problem: The form wasn't saving the person editing the form into the m2m relationship by default.
@login_required
# only owner can edit this
# use edit view?
def edit_project(request,id):
    project = Project.objects.get(id=id)
    context = {
        'project':project,
    }
    if request.method == 'GET':
        # TODO: Make form
        form = ProjectEditForm(request.user,instance = project)
        # TODO: make URL
        context['form']=form
        return render(request,'assemble/project_edit_form.html',context)
    elif request.method =='POST':
        form = ProjectEditForm(request.user,request.POST,instance=project)
        if form.is_valid():
            is_me = Profile.objects.get(user=request.user)
            form.save()
            messages.success(request,f"Edited the project '{project.name}'.")
            return redirect('project-list')
"""

@login_required
# both components and tasks are shared in the same model, query by id
def edit_component_or_task(request,id):
    context={}
    component = ProjectComponent.objects.get(id=id)
    context['component'] = component
    if request.method == "GET":
        form = ComponentEditForm(instance=component)
        context['form'] = form
        return render(request,'assemble/edit_component_form.html',context)
    elif request.method == 'POST':
        form = ComponentEditForm(request.POST,instance=component)
        if form.is_valid():
            form.save()
            messages.success(request,f"Successfully edited '{component}'")
            return redirect('project-detail',project_slug =component.project.slug)


class ProjectEditView(LoginRequiredMixin,UpdateView):
    model = Project
    form_class = ProjectEditForm
    template_name = 'assemble/project_edit_form.html'
    success_url = reverse_lazy('project-list')

    def get_form_kwargs(self):
        kwargs = super(ProjectEditView,self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # saves the user editing the form into the project's user field.
    def form_valid(self, form):
        is_me = Profile.objects.get(user=self.request.user)
        super().form_valid(form)
        form.instance.user.add(is_me)
        # needs to return a HttpResponse Object
        # before it returned super().form_valid(form)
        # however when using a m2m relationship, the object needs to be saved FIRST, then relationships can be made.
        messages.success(self.request, f"Edited {form.instance.name}")
        return redirect('project-list')
