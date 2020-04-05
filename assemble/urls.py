from django.urls import path,re_path
from django.contrib.auth import views as auth_views
from . import views


# think of consistent URL patterns, mine are all over the place!

urlpatterns = [
    path('project-list/project-detail/ajax/<project_slug>/',views.project_detail_ajax,name="project-detail-ajax"),
    path('',views.index,name='home'),

    ############################################
    ### USER AUTH VIEWS
    ############################################
    path('accounts/sign-up',views.sign_up,name='sign-up'),
    path('logout',views.log_out,name='logged_out'),


    ############################################
    ### PROJECT URLS
    ############################################
    path('project-list/',views.ProjectList.as_view(),name="project-list"),
    path('project-create/',views.ProjectCreate.as_view(),name="project-create"),
    path('project-list/project-detail/<project_slug>/',views.project_detail_view,name="project-detail"),
    path('project-list/delete-project/<pk>/',views.delete_project,name='delete-project'),
    path('project-list/edit-project/<pk>/',views.ProjectEditView.as_view(),name='edit-project'),
    path('project-list/project-detail/history/<pk>/',views.history_view,name='project-history'),

    # displays the current project component and all project component tasks
    #path('project-component-detail/<project_component_slug>/',project_component_detail_view,name="project-component-detail"),

    ############################################
    ### PROJECT COMPONENT/TASK URLS
    ############################################
    path('project-list/project-detail/project-component-create/<project_slug>/',views.ProjectComponentCreate.as_view(),
    name="project-component-create"),
    
    path('project-list/project-detail/edit-details/<pk>/',views.edit_component_or_task,name="edit-details"),
    path('finish-task/<pk>/',views.finish_task_detail,name="finish-task"),
    path('delete-task/<pk>/',views.delete_task,name="delete-task"),

    ############################################
    ### USER PROFILE AND INTERACTION URLS
    ############################################
    path('profile/',views.profile,name='profile'),
    path('search/',views.search_user,name="search-user"),
    path('search/profile/<slug>/',views.profile_view,name="profile-view"),

    path('search/send-friend-request/<sent_to>/',views.send_friend_request,name="send-friend-request"),
    path('profile/accept-friend-request/<from_user>/',views.accept_friend_request,name='accept-friend-request'),
    path('profile/delete-friend-request/<pk>/',views.delete_friend_request,name="delete-friend-request"),

    ############################################
    ### AJAX VIEWS
    ############################################
    path('ajax/delete-task/',views.delete_task_ajax,name="delete-task-ajax"),
    path('ajax/edit-task/',views.edit_task_ajax,name="edit-task-ajax"),
    path('ajax/component-task-create/',views.add_task_ajax,name='create-task-ajax'),
    path('ajax/finish-task-test/',views.finish_task_ajax,name="finish-task-ajax"),
]
