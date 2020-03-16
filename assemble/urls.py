from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    sign_up,index,
    ProjectList,
    ProjectCreate,
    project_detail_view,
    #project_component_detail_view,
    ProjectComponentCreate,
    ProjectTaskCreate,
    #component_task_detail,
    finish_task_detail,
    delete_task,
    profile,
    search_user,
    send_friend_request,
    profile_view,
    accept_friend_request,
    delete_friend_request,
    delete_project,
    #edit_project,
    edit_component_or_task,
    ProjectEditView,
    log_out
    
    )

# think of consistent URL patterns, mine are all over the place!

urlpatterns = [
    path('',index,name='home'),
    
    ############################################
    ### USER AUTH VIEWS
    ############################################
    path('accounts/sign-up',sign_up,name='sign-up'),
    path('logout',log_out,name='logged_out'),
    

    ############################################
    ### PROJECT URLS
    ############################################
    path('project-list/',ProjectList.as_view(),name="project-list"),
    path('project-create/',ProjectCreate.as_view(),name="project-create"),
    path('project-list/project-detail/<project_slug>/',project_detail_view,name="project-detail"),
    path('project-list/delete-project/<pk>/',delete_project,name='delete-project'),
    path('project-list/edit-project/<pk>/',ProjectEditView.as_view(),name='edit-project'),

    # displays the current project component and all project component tasks
    #path('project-component-detail/<project_component_slug>/',project_component_detail_view,name="project-component-detail"),

    ############################################
    ### PROJECT COMPONENT/TASK URLS
    ############################################
    path('project-list/project-detail/project-component-create/<project_slug>/',ProjectComponentCreate.as_view(),name="project-component-create"),
    path('project-list/project-detail/component-task-create/<project_component_slug>/',ProjectTaskCreate.as_view(),name='create-task'),
    path('project-list/project-detail/edit-details/<pk>/',edit_component_or_task,name="edit-details"),
    path('finish-task/<pk>/',finish_task_detail,name="finish-task"),
    path('delete-task/<pk>/',delete_task,name="delete-task"),

    #path('project-component-detail/<project_component_slug>/<component_task_slug>/',component_task_detail,name="component-task-detail"),
    

    ############################################
    ### USER PROFILE AND INTERACTION URLS
    ############################################
    path('profile/',profile,name='profile'),
    path('search/',search_user,name="search-user"),
    path('search/profile/<slug>/',profile_view,name="profile-view"),

    path('search/send-friend-request/<sent_to>/',send_friend_request,name="send-friend-request"),
    path('profile/accept-friend-request/<from_user>/',accept_friend_request,name='accept-friend-request'),
    path('profile/delete-friend-request/<pk>/',delete_friend_request,name="delete-friend-request"),

    

    
    
       
]

