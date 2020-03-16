from django.contrib import admin
from .models import Project,ProjectComponent,Profile,FriendRequest,UserFeedback
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.


admin.site.register(Project,SimpleHistoryAdmin)
admin.site.register(ProjectComponent,SimpleHistoryAdmin)
admin.site.register(FriendRequest,SimpleHistoryAdmin)
admin.site.register(Profile,SimpleHistoryAdmin)
admin.site.register(UserFeedback,SimpleHistoryAdmin)

