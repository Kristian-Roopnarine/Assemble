from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models.signals import post_save

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


class ProjectComponent(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200,blank=True)
    slug = models.SlugField(max_length=100,unique=True,blank=True,null=True)
    completed = models.BooleanField(default=False)
    task = models.ForeignKey('self',null=True,default=None,related_name="component",on_delete=models.CASCADE)
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