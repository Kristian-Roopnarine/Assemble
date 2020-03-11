from django.contrib import admin
from .models import Project,ProjectComponent,ComponentTask
# Register your models here.
admin.site.register(Project)
admin.site.register(ProjectComponent)
admin.site.register(ComponentTask)