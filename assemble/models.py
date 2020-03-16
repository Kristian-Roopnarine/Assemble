from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models.signals import post_save
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
    description = models.CharField(max_length=200,blank=True) # can change this
    slug = models.SlugField(max_length=100,unique=True,blank=True,null=True)
    completed = models.BooleanField(default=False) # can change this
    task = models.ForeignKey('self',null=True,default=None,related_name="component",on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    history = HistoricalRecords()


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
    first = history_records.pop(0)
    for record in history_records:
        first |= record
    return first.order_by('-history_date')

def create_strings_from_queryset(ordered_queryset):
    """
    :param ordered_queryset: Takes in an ordered Historical queryset
    :return: A list of lists containing two items, string to be displayed and date.
    """
    render_list = []
    for record in ordered_queryset:
        if record.prev_record:
            # if this item has been edited
            diff = record.diff_against(record.prev_record)
            user = record.history_user
            changes = diff.changes[0]
            field = changes.field
            old = changes.old
            new = changes.new
            date = record.history_date.strftime('%b/%d/%Y %H:%M')
            if field == "name" or field == "description":
                render_list.append([f"{user} changed the {field} from '{old}' to '{new}'",date])
            else:
                #field changed was completed
                render_list.append([f"{user} changed the completed status of "
                                    f"'{record.history_object}' from {old} to "
                                    f"{new}",
                                    date])
        else:
            user = record.history_user
            date = record.history_date.strftime('%b/%d/%Y %H:%M')
            component = record.name
            project = record.project
            if record.task == None:
                render_list.append([f"{user} added the component '{component}' to '{project}'",
                                    date])
            else:
                project_component = record.task
                render_list.append([f"{user} added the task '{component}' to '{project_component}'",
                                    date])
    print(render_list)
    return render_list
