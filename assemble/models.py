from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=60)
    description = models.TextField(max_length=400)
    user = models.ManyToManyField(User)
    slug = models.SlugField(max_length=100,unique=True,blank=True,null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    # create unique slug
    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while Project.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{num}"
            num += 1
        return unique_slug
    
    #overwrite the save method to create a slug
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args,**kwargs)

class ProjectComponent(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    completed = models.BooleanField(default=False)
    slug = models.SlugField(max_length=100,unique=True,blank=True,null=True)
    belongs_to = models.ForeignKey(Project,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

    # create unique slug
    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while ProjectComponent.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{num}"
            num += 1
            return unique_slug
    
    #overwrite the save method to create a slug
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args,**kwargs)    

    