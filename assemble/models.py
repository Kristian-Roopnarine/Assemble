from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models.signals import post_save,pre_save,pre_delete,post_delete,m2m_changed
from simple_history.models import HistoricalRecords

"""
Project
    owner - person who created the project ( one owner, but owner may be linked to other projects)
    users - people working on the project (many users may be working on this project)
    description
    name
    slug
    completed

Profile
    user - only one user per profile
    friends - profile is linked or has relationships with other profiles.

"""

class Project(models.Model):
    name = models.CharField(max_length=60)
    description = models.TextField(max_length=400)
    user = models.ManyToManyField('Profile',blank=True)
    owner = models.ForeignKey('Profile',blank=True,on_delete=models.CASCADE,related_name="creator")
    # these many parameters because of how the m2m is saved
    # the model needs to be saved first THEN we can define relationships
    # because of that, the model is saved with a slug field that is empty at first

    slug = models.SlugField(max_length=100,unique=True,blank=True,null=True)
    completed= models.BooleanField(default=False)
    history = HistoricalRecords()


    def __str__(self):
        return self.name

    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while Project.objects.filter(slug=unique_slug).exists():
            unique_slug=f"{slug}-{num}"
            num += 1
        return unique_slug

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=self._get_unique_slug()
        super().save(*args,**kwargs)

    def get_absolute_url(self):
        return reverse('project-detail',kwargs={'project_slug':self.slug})

# can return all project components from a project using
# test_project.projectcomponent_set.all() --> From parent to child with foreign key relationship

class ProjectComponent(models.Model):
    name = models.CharField(max_length=200) # can change this
    slug = models.SlugField(max_length=100,unique=True,blank=True,null=True)
    completed = models.BooleanField(default=False) # can change this
    task = models.ForeignKey('self',null=True,default=None,related_name="component",
                             on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    history = HistoricalRecords()

    __original_name = None
    __original_status = None

    def __str__(self):
        return self.name

    def __init__(self,*args,**kwargs):
        """Calls super() which calls the init function of ProjectComponent, then sets __original_name = name."""
        super(ProjectComponent,self).__init__(*args,**kwargs)
        self.__original_name = self.name

        # this line makes the task_finish_detail view work
        # before it wasn't registering when completed went from true to false but the tests were working
        self.__original_status = self.completed

    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while ProjectComponent.objects.filter(slug=unique_slug).exists():
            unique_slug=f"{slug}-{num}"
            num += 1
        return unique_slug

    def save(self,*args,**kwargs):
        """If self.name has been changed(via edit) then created a project history"""

        if self.name != self.__original_name:
            ProjectHistory.objects.create(before=self.__original_name,after=self.name,project=self.project)

        if self.__original_status != self.completed:
            # changed from false to true or true to false

            ProjectHistory.objects.create(before=f"'{self.name}' changed to {self.completed}.",after="status",project=self.project)

        if not self.slug:
            self.slug=self._get_unique_slug()

        
        super().save(*args,**kwargs)
        self.__original_status = self.completed
        self.__original_name = self.name
        

    def get_absolute_url(self):
        return reverse('project-detail',kwargs={'project_slug':self.project.slug})



class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    slug = models.SlugField(blank=True)
    friends = models.ManyToManyField('Profile',blank=True)
    history = HistoricalRecords()


    def __str__(self):
        return self.user.username

    def _get_unique_slug(self):
        slug = slugify(self.user.username)
        unique_slug = slug
        num = 1
        while Profile.objects.filter(slug=unique_slug).exists():
            unique_slug=f"{slug}-{num}"
            num += 1
        return unique_slug

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=self._get_unique_slug()
        super().save(*args,**kwargs)

def post_save_user_model_receiver(sender,instance,created,*args,**kwargs):
    if created:
        try:
            Profile.objects.create(user=instance)
        except:
            pass

#creates a profile for every user on sign up
post_save.connect(post_save_user_model_receiver,sender=User)

class FriendRequest(models.Model):
    to_user = models.ForeignKey(User,related_name = 'to_user',on_delete=models.CASCADE)
    from_user = models.ForeignKey(User,related_name ='from_user',on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.from_user} to {self.to_user}. Sent {self.timestamp}"


class UserFeedback(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    date_recorded = models.DateTimeField()

    def __str__(self):
        return self.title

class ProjectHistory(models.Model):
    # if the history object is being created then the before field will be empty.
    before = models.TextField(max_length=100,blank=True,null=True)
    after  = models.TextField(max_length=100,blank=True,null=True)
    date_changed = models.DateTimeField(auto_now_add=True)

    # might have to change the save method to include the profile
    user = models.ForeignKey(Profile,on_delete=models.CASCADE,blank=True,null=True)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    list_string = None

    #it works for creating!
    def __init__(self,*args,**kwargs):
        super(ProjectHistory,self).__init__(*args,**kwargs)
        self.create_history_string()

    # maybe add a method to return a string of the fields to display?
    # -- will need name of user
    # -- was it an edit,create or delete
    # -- project name
    # -- before and after value

    #### Possible signals to use ################################
    # post_save, pre_save, post_delete, pre_delete, m2m_changed #
    #############################################################

    """
    pre_save(sender,instance,raw,using,update_fields):
    This is sent at the beginning of a model's save method
        sender- the model class
        instance- the actual instance being saved
        raw - A boolean; True if the model is saved exactly as presented
        using- the database alias being used
        update_fields - the set of fields to update as passed to Model.save() or None if update_fields wasn't passed.

    post_save(sender,instance,raw,using,update_fields)
    This is sent at the end of the save method
        sender - the model class
        instance- the actual instance being saved
        created  -  A boolean, True if a new record is created
        raw - same as pre_save
        using - ""
        updated_fields - ""

    pre_delete(sender,instance,using):
    Sent at the beginning of a models delete() method and a queryset's delete() method

        sender- the model class
        instance - the actual instance being deleted
        using - ""

    post_delete(sender,instance,using):
    Sent at the end of a model's delete() and a queryset's delete9) method.

        sender - the model class
        instance - the actual instance being deleted. Note that the object will no longer be in the database.
        using - the database alias being used

    m2m_changed(sender,instance,action,reverse,model,pk_set,using):
    Sent when a ManyToManyField is changed on a model instance. Strictly speaking, this is not a model signal since it is sent by the ManyToManyField, but it complements the pre_save/post_save and pre_delete/post_delete when it comes to tracking changes to models.

        sender - The immediate model calss describing the ManyToManyField. This class is automatically created when a many-to-many field is defined; you can access it using thr though attribute on the many-to-many-field.
        instance- the instance whose many-to-many relation is updated. This can be an instance of the sender, or of the class the m2m is related to.
        action- a string indicating the type of update that is done to the relationship.
            "pre_add" - sent before one or more objects are added to the relation.
            "post_add" - sent after one or more objects are added to the relation.
            "pre_remove" - sent ebfore one or more objects are removed from the relation.
    """

    def create_history_string(self):
        """
        When a ProjectHistory instance is created, generate a string to be displayed on Assemble based on the action of the component/task.
        """
        if self.before == None:
            self.list_string = f"'{self.after}' was created."
        elif self.after == 'deleted':
            # it was deleted
            self.list_string = f"'{self.before}' was deleted."
        elif self.after == 'status':
            # task status was changed
            self.list_string = self.before
        else:
            self.list_string = f"'{self.before}' was edited to '{self.after}'."


    def __str__(self):
        return self.list_string

def pre_delete_project_component_model_reciever(sender,instance,*args,**kwargs):
    """ Detects when a project component is deleted and creates a ProjectHistory instance."""
    ProjectHistory.objects.create(before=instance.name,after='deleted',project=instance.project)

def post_save_project_component_model_reciever(sender,instance,created,*args,**kwargs):
    """Detects when a project component is created and creates a ProjectHistory instance.

    Arguments:
        sender {[class]} -- [the model class]
        instance {[class]} -- [the instance being created]
        created {[boolean]} -- [True or False, whether the instance was created]
    """
    if created:
        try:
            ProjectHistory.objects.create(after=instance.name,project=instance.project)

        except:
            pass

# it worked on a project component
post_save.connect(post_save_project_component_model_reciever,sender=ProjectComponent)
pre_delete.connect(pre_delete_project_component_model_reciever,sender=ProjectComponent)

def get_list_of_project_component_history_records(project):
    """
    :param project:  A project model object that has been queried.
    :return: A list of historical record queryset for each component
    """
    return [test.history.all() for test in project.projectcomponent_set.all()]
"""
def get_historical_differences(history_records):
    reverse_sorted = []
    for records in history_records:
        # has more that one record history
        if records.count()>1:
            for small in records:
                # need this value print(f"\t\t{small.history_user}")
                # maybe need this value print(f"\t\t{small.history_type}")
                # need this value print(f"\t\t{small.prev_record.history_object}")
                # need this value print(f"\t\t{small.history_object}") --> returns the project
                # component
                try:
                    diff = small.diff_against(small.prev_record)
                    for change in diff.changes:
                        if change.field == 'name':
                            reverse_sorted.append([f"{small.history_user} changed the task name "
                                                   f"from '{change.old}' "
                                  f"to '{change.new}' on ",
                                                  small.history_date.strftime('%b/%d/%Y %H:%M')])

                        else:
                            reverse_sorted.append([f"{small.history_user} changed the task's "
                                  f"'{small.history_object}' completed status "
                                  f"from "
                                  f"{change.old} to {change.new} on ",
                                                   small.history_date.strftime('%b/%d/%Y %H:%M')])
                except TypeError:
                    pass
        else:
            for record in records:
                if record.task == None:
                    reverse_sorted.append([f"{record.history_user} added the component "
                                           f"'{record.name}' to "
                          f"{record.project} on ",record.history_date.strftime('%b/%d/%Y %H:%M')])
                else:
                    reverse_sorted.append([f"{record.history_user} added the task "
                                            f"'{record.name}' to the component "
                          f"'{record.task}' on ",record.history_date.strftime('%b/%d/%Y %H:%M')])

    reverse_sorted.reverse()
    return reverse_sorted
"""

def join_queryset_of_historical_records(history_records):
    """
    :param history_records: List of historical record queryset for each component
    :return: An ordered union of querysets
    """
    try:
        first = history_records.pop(0)
        for record in history_records:
            first |= record
        return first.order_by('-history_date')
    except IndexError:
        return 0

def create_strings_from_queryset(ordered_queryset):
    """
    :param ordered_queryset: Takes in an ordered Historical queryset
    :return: A list of lists containing two items, string to be displayed and date.
    """
    if ordered_queryset != 0:
        render_list = []
        for record in ordered_queryset:
            user = record.history_user
            date = record.history_date.strftime('%b/%d/%Y %H:%M')
            component = record.name
            project = record.project
            if record.prev_record:
                # if this item has been edited
                diff = record.diff_against(record.prev_record)
                user = record.history_user
                try:
                    changes = diff.changes[0]
                except IndexError:
                    continue
                field = changes.field
                old = changes.old
                new = changes.new

                if field == "name" or field == "description":
                    render_list.append([f"{user} changed the {field} from '{old}' to '{new}'",date])
                else:
                    #field changed was completed
                    render_list.append([f"{user} changed the completed status of "
                                        f"'{record.history_object}' from {old} to "
                                        f"{new}",
                                        date])
            else:
                if record.task == None:
                    render_list.append([f"{user} added the component '{component}' to '{project}'",
                                        date])
                else:
                    project_component = record.task
                    render_list.append([f"{user} added the task '{component}' to '{project_component}'",
                                        date])
        return render_list
    else:
        return 0
