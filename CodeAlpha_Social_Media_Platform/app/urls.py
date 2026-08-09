from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('create-post/', views.create_post, name='create_post'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('edit-post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('search/', views.search_users, name='search_users'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('notifications/', views.notifications, name='notifications'),
    path("inbox/", views.inbox, name="inbox"),
path("chat/<str:username>/", views.chat, name="chat"),
]

