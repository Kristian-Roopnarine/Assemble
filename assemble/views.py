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


############################################
### USER AUTHENTIFICATION VIEWS
############################################
# home
@login_required
def index(request):
    """
    The home page view which requires a login. If the user is not logged in, they are redirected to the login page.
    
    Arguments:
        request {dictionary} -- [Either GET or POST]
    
    Returns:
        [HttpResponse] -- [Points our view to a template to be rendered with the appropriate request.]
    """
    return render(request,'assemble/index.html')

# sign up view
def sign_up(request):
    """The view responsible for handling the sign up template
    
    Arguments:
        request {Http response} -- [GET or POST]
    
    Returns:
        [HttpResponse] -- [In a GET request it loads an empty form. POST requests fill the form with data]
    """
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
    """The view responsible for logging a user out. Displays a UserFeedback form to the user to optionally fill out.
    
    Arguments:
        request {Http response} -- [GET or POST]
    
    Returns:
        [http response] -- [Either redirects to the home page after a successful POST request or just the regular log out page.]
    """
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


############################################
### PROJECT VIEWS
############################################

# List view of all the projects for a user
class ProjectList(LoginRequiredMixin,ListView):
    """
    A class based view responsible for querying a list of Projects from the database.
    It inherits from LoginRequiredMixin to not allow anonymous users to view the information.
    
    Arguments:
        LoginRequiredMixin {class} -- [requires user to be logged in to view information]
        ListView {class} -- [class that produces the queryset]
    
    Returns:
        [project_list.html] -- [template that renders the list of projects for a user.]
    """
    model = Project
    
    # i think I can turn this into one line
    # I'm using the request data to pull my user instance from it
    # getting the profile with that user instance
    # getting the projects associated with that profile
    def get_queryset(self):
        """
        Alter the get_queryset method to specify the queryset to return from the view set.
        
        Returns:
            [Project model] -- [Returns a queryset of projects for the user signed in.]
        """
        is_me = Profile.objects.get(user=self.request.user)
        return Project.objects.filter(user=is_me)

# view to create more projects
class ProjectCreate(LoginRequiredMixin,CreateView):
    """
    A class based view that creates a form from our Project ModelForm.
    
    Arguments:
        LoginRequiredMixin {class} -- [requires our user to be logged in to create projects]
        CreateView {class} -- [generates form from specified class]
    
    Returns:
        [http response] -- [After checking the form for errors, saves it and redirects to a specific page. Either set by success_url or a models get_absolute_url method.]
    """
    form_class = ProjectCreateForm
    template_name = "assemble/project_form.html"
    success_url = reverse_lazy('project-list')

    # addings key word arguments to this class
    # in this case we're adding the user
    def get_form_kwargs(self):
        """
        Overide the get_form_kwargs method inherited from CreateView.
        
        Returns:
            [kwargs:key word arguments] -- [Key word arguments to build the model form]
        """
        kwargs = super(ProjectCreate,self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self,form):
        """
        Overiding the form_valid method inherited from CreateView.
        I had to over ride the default method because we are saving many-to-many-relationships in this model.
        According to Django documentation, to save m2m relationships the data needs to be saved FIRST, then relationships can be added.
        
        Arguments:
            form {form} -- [The form being passed into the function.]
        
        Returns:
            [http response] -- [If the form has no errors, redirects to another page.]
        """
        is_me = Profile.objects.get(user=self.request.user)
        form.instance.owner=is_me
        super().form_valid(form)
        form.instance.user.add(is_me)
        # needs to return a HttpResponse Object
        # before it returned super().form_valid(form)
        # however when using a m2m relationship, the object needs to be saved FIRST, then relationships can be made.
        messages.success(self.request,f"Created {form.instance.name}")
        return redirect('project-list')

@login_required
def project_detail_view(request,project_slug):
    """
    The view for displaying the components of a specific project.
    
    Arguments:
        request {dictionary} -- [GET or POST]
        project_slug {slugfield} -- [The project's slug field passed in from anchor tags in the project-list template.]
    
    Returns:
        [http response] -- [Displays that project to the user with all the active components.]
    """

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
def delete_project(request,id):
    """
    View responsible for deleting a project from the project-list template.
    
    Arguments:
        request {dictionary} -- [GET or POST]
        id {primary key} -- [Primary key of the project to be deleted.]
    
    Returns:
        [http response] -- [response that redirects to the project-list]
    """
    project = Project.objects.get(id=id)
    context = {
        'project':project
    }
    if request.method == "GET":
        return render(request,'assemble/delete.html',context)
    elif request.method == 'POST':
        project.delete()
        return redirect('project-list')

class ProjectEditView(LoginRequiredMixin,UpdateView):
    """
    Class based view used to generate an update form for projects. 
    
    Arguments:
        LoginRequiredMixin {class} -- [Inherit from this class to prevent anonymous users from accessing information.]
        UpdateView {class} -- [class to create the update form from the Project model class]
    
    Returns:
        [http response] -- [if form is successfully saved then the user is redirected to the project-list view.]
    """
    model = Project
    form_class = ProjectEditForm
    template_name = 'assemble/project_edit_form.html'
    success_url = reverse_lazy('project-list')

    def get_form_kwargs(self):
        """
        Overriding the default get_form_kwargs to add the user editing the form.
        
        Returns:
            [key word arguments] -- [dictionary containing information for the form]
        """
        kwargs = super(ProjectEditView,self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # saves the user editing the form into the project's user field.
    def form_valid(self, form):
        """
        Overriding default form_valid method. This is to ensure that the user editing the form is still saved as a user in the Project.
        
        Arguments:
            form {form} -- [The ProjectUpdateForm.]
        
        Returns:
            [http response] -- [returns the user to the project-list view if the form is successfully saved.]
        """
        is_me = Profile.objects.get(user=self.request.user)
        super().form_valid(form)
        form.instance.user.add(is_me)
        # needs to return a HttpResponse Object
        # before it returned super().form_valid(form)
        # however when using a m2m relationship, the object needs to be saved FIRST, then relationships can be made.
        messages.success(self.request, f"Edited {form.instance.name}")
        return redirect('project-list')




############################################
### PROJECT COMPONENT/TASK VIEWS
############################################


# view to create project components
class ProjectComponentCreate(LoginRequiredMixin,CreateView):
    """
    Class based view responsible for creating project components.
    
    Arguments:
        LoginRequiredMixin {class} -- [Class that requires our user to login to add components.]
        CreateView {class} -- [Class that creates a form from ProjectComponent ModelForm]
    
    Returns:
        [http response] -- [If the form is saved successfully redirects the user to the project-detail.]
    """
    model = ProjectComponent
    fields = ['name','description']
    
    def form_valid(self,form):
        """
        Overriding the default form_valid method. This adds the component as a child of the parent project.
        
        Arguments:
            form {form} -- [ProjectComponentCreate form]
        
        Returns:
            [http response] -- [redirects the user to the project-detail page if successful.]
        """
        project = Project.objects.get(slug=self.kwargs['project_slug'])
        form.instance.project = project
        super().form_valid(form)
        messages.success(self.request,f"Added '{form.instance.name}' to {project.name}")

        # this takes the models get_absolute_url and redirects to the URL
        return redirect(project)
    
    def get_context_data(self,**kwargs):
        """
        Over ride the get_context_data method. We pass in the parent project to display that information in our form.
        
        Returns:
            [dictionary] -- [key values pairs of information to present in the template]
        """
        context= super().get_context_data(**kwargs)
        project = Project.objects.get(slug=self.kwargs['project_slug'])
        context['project'] = project
        return context

class ProjectTaskCreate(LoginRequiredMixin,CreateView):
    """
    A class based view to create a form to create child tasks to parent components.
    
    Arguments:
        LoginRequiredMixin {[class]} -- [Requires our users to be logged in.]
        CreateView {[class]} -- [Creates the form]
    
    Returns:
        [http response] -- [if successful, will redirect user to project-detail view.]
    """
    model = ProjectComponent
    fields = ['name']
    template_name = "assemble/componenttask_form.html"

    def form_valid(self,form):
        """
        Overriding the default form_valid method to save relationships. Adds the relationship of parent component to the child task. Adds the task as a child to the project. The form opens up as a modal in the project-detail view.
        
        Arguments:
            form {form} -- [ProjectTaskCreate form created from form in forms.py.]
        
        Returns:
            [http response] -- [if successful redirects the user to the project-detail.]
        """
        component = ProjectComponent.objects.get(slug=self.kwargs['project_component_slug'])
        form.instance.project = component.project
        form.instance.task = component
        super().form_valid(form)
        messages.success(self.request,f"Added '{form.instance.name}' to '{form.instance.task}'")
        return redirect('project-detail',project_slug=component.project.slug)
    
    def get_context_data(self,**kwargs):
        """
        Queries the DB for information about the project component to pass into the form.
        
        Returns:
            [dictionary] -- [key values pairs of information to display in the componenttask_form.html.]
        """
        context= super().get_context_data(**kwargs)
        component = ProjectComponent.objects.get(slug=self.kwargs['project_component_slug'])
        context['component'] = component
        return context



# view tasks of a component
# do I even use this
# reconsider
"""
@login_required
def project_component_detail_view(request,project_component_slug):
    component = ProjectComponent.objects.get(slug=project_component_slug)
    component_tasks = component.component.all()
    context = {
        'component_tasks':component_tasks,
        'component':component,
    }
    return render(request,'assemble/project_component.html',context)


@login_required
#reconsider using this
def component_task_detail(request,project_component_slug,component_task_slug):
    return render(request,'assemble/task_detail.html')
"""

@login_required
def finish_task_detail(request,pk):
    """
    Changes the completed field of a task to the opposite.
    
    Arguments:
        request {[http response]} -- [GET or POST]
        pk {[int]} -- [Primary key of the task]
    
    Returns:
        [http response] -- [redirects the user to project-detail.]
    """
    task = get_object_or_404(ProjectComponent,id=pk)
    before=task.completed
    task.completed= not before
    task.save()
    messages.success(request,f"The task '{task}' completed status was changed to {task.completed}.")
    return redirect(task.project)

@login_required
def delete_task(request,pk):
    """
    View responsible for deleting a task.
    
    Arguments:
        request {[http response]} -- [GET or POST]
        pk {[int]} -- [primary key of the task being deleted.]
    
    Returns:
        [type] -- [description]
    """
    task = get_object_or_404(ProjectComponent,id=pk)
    messages.success(request,f"Successfully deleted {task}")
    task.delete()
    return redirect(task.project)

@login_required
# both components and tasks are shared in the same model, query by id
def edit_component_or_task(request,pk):
    """
    View responsible for editing a component or task.
    
    Arguments:
        request {[http response]} -- [GET or POST request]
        pk {[int]} -- [Primary key of the object being edited]
    
    Returns:
        [http response] -- [If get request, returns a response containing a prefilled form. If POST request and the form is saved, user is redirected to project-detail.]
    """
    context={}
    component = ProjectComponent.objects.get(id=pk)
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


############################################
### USER INTERACTION VIEWS
############################################
@login_required
def profile(request):
    """
    Loads the user profile containing current projects, friends and friend requests.
    
    Arguments:
        request {[http response]} -- [GET or POST request]
    
    Returns:
        [dictionary] -- [key values pairs that determine the information displayed in the template profile.html]
    """
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
    """
    View responsible for loading another user's profile after searching.
    
    Arguments:
        request {[http response]} -- [GET or POST request]
        slug {[slugfield]} -- [The slug of the user being searched for. Maybe use id instead?]
    
    Returns:
        [dictionary] -- [dictionary containing details about whether or not you're friend with the user or whether you already sent them a friend request.]
    """
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
    """
    View responsible for presenting user's from the search form.
    
    Arguments:
        request {[http response]} -- [GET or POST]
    
    Returns:
        [http response] -- [If the user that was searched is you, redirects to your profile. Otherwise it returns the user being searched.]
    """
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
    """
    View responsible for creating a FriendRequest object.
    
    Arguments:
        request {[http response]} -- [GET or POST]
        sent_to {[user]} -- [The profile where you sent the friend request to. ]
    
    Returns:
        [http response] -- [redirects user to the sent_to user's profile with updated buttons.]
    """
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
    """
    View responsible for accepting friend requests from the user profile.
    
    Arguments:
        request {[http response]} -- [get or post]
        from_user {[user]} -- [The profile of the person who sent the friend request.]
    
    Returns:
        [http response] -- [If the request is successful it redirects to deleting the friend request.]
    """
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
def delete_friend_request(request,pk):
    """
    View responsible for deleting friend requests from the user profile.
    
    Arguments:
        request {[http response]} -- [get or post]
        from_user {[user]} -- [The profile of the person who sent the friend request.]
    
    Returns:
        [http response] -- [If the request is successful it redirects to the users profile.]
    """
    frequest= FriendRequest.objects.get(id=pk)
    frequest.delete()
    # delete
    # redirect to user profile
    return redirect('profile')



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




