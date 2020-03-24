from django.contrib import admin
from .models import Project,ProjectComponent,Profile,FriendRequest,UserFeedback,ProjectHistory

# Register your models here.


admin.site.register(Project)
admin.site.register(ProjectComponent)
admin.site.register(FriendRequest)
admin.site.register(Profile)
admin.site.register(UserFeedback)
admin.site.register(ProjectHistory)

