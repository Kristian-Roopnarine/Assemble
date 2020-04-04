from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models.signals import post_save,pre_save,pre_delete,post_delete,m2m_changed


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

    def __str__(self):
        return self.name


    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while ProjectComponent.objects.filter(slug=unique_slug).exists():
            unique_slug=f"{slug}-{num}"
            num += 1
        return unique_slug

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=self._get_unique_slug()
        super().save(*args,**kwargs)



    def get_absolute_url(self):
        return reverse('project-detail',kwargs={'project_slug':self.project.slug})



class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    slug = models.SlugField(blank=True)
    friends = models.ManyToManyField('Profile',blank=True)

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
    previous_field = models.CharField(max_length=200,blank=True)
    updated_field = models.CharField(max_length=200,blank=True)
    date_changed = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,null=True)
    # might have to change the save method to include the profile
    user = models.CharField(max_length=100,null=True,blank=True)
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
    # this is getting called twice when creating a component.
    # the logic is the issue

    def __str__(self):
        return self.list_string

    def create_history_string(self):
        if self.status == "deleted":
            self.list_string= f"{self.previous_field} was {self.status} by {self.user}."
        elif self.status == "edited":
            self.list_string= f"{self.previous_field} was {self.status} to {self.updated_field} by {self.user}."
        elif self.status == "updated to true":
            self.list_string = f"{self.previous_field} was updated to complete by {self.user}."
        elif self.status == "updated to false":
            self.list_string = f"{self.previous_field} was updated to uncompleted by {self.user}."
        elif self.status == "created":
            self.list_string= f"{self.previous_field} was created by {self.user}."


def get_list_of_project_component_history_records(project):
    """
    :param project:  A project model object that has been queried.
    :return: A list of historical record queryset for each component
    """
    return [test.history.all() for test in project.projectcomponent_set.all()]


