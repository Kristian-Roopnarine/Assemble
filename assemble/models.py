from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

class Project(models.Model):
    name = models.CharField(max_length=60)
    description = models.TextField(max_length=400)
    user = models.ManyToManyField(User)

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
        return reverse('project-component-detail',kwargs={'project_component_slug':self.slug})




    