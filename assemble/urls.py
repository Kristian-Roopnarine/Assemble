from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    sign_up,index,
    ProjectList,
    ProjectCreate,
    project_detail_view,
    project_component_detail_view,
    ProjectComponentCreate,
    ProjectTaskCreate,
    component_task_detail,
    finish_task_detail,
    delete_task,
    profile,
    search_user,
    send_friend_request,
    profile_view
    
    )

urlpatterns = [
    path('',index,name='home'),
    path('accounts/sign-up',sign_up,name='sign-up'),
    path('project-list/',ProjectList.as_view(),name="project-list"),
    path('project-create/',ProjectCreate.as_view(),name="project-create"),

    # displays the current project and all project components
    path('project-detail/<project_slug>/',project_detail_view,name="project-detail"),

    # displays the current project component and all project component tasks
    path('project-component-detail/<project_component_slug>/',project_component_detail_view,name="project-component-detail"),

    #create components for a specific project
    path('<project_slug>/project-component-create/',ProjectComponentCreate.as_view(),name="project-component-create"),
    # displays one task
    path('project-component-detail/<project_component_slug>/<component_task_slug>/',component_task_detail,name="component-task-detail"),
    
    # create tasks for a component
    path('<project_component_slug>/component-task-create/',ProjectTaskCreate.as_view(),name='create-task'),

    #updates task completed
    path('finish-task/<id>/',finish_task_detail,name="finish-task"),
    path('delete-task/<id>/',delete_task,name="delete-task"),
    path('profile/',profile,name='profile'),
    path('search/',search_user,name="search-user"),

    path('search/send-friend-request/<sent_to>/',send_friend_request,name="send-friend-request"),
    path('search/profile/<slug>/',profile_view,name="profile-view")
    
    
]