from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Profile, Post, Comment, Like, Follow, Notification, Message
from .forms import ProfileForm


# ---------------- HOME ----------------

def home(request):
    posts = Post.objects.all().order_by('-created_at')

    following = []

    if request.user.is_authenticated:
        following = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)

    context = {
        "posts": posts,
        "following": following,
    }

    return render(request, "index.html", context)


# ---------------- REGISTER ----------------

def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Registration Successful!")
        return redirect("login")

    return render(request, "register.html")


# ---------------- LOGIN ----------------

def login_user(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful!")
            return redirect("home")

        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, "login.html")


# ---------------- LOGOUT ----------------

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")


# ---------------- PROFILE ----------------

@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    posts = Post.objects.filter(
        user=request.user
    ).order_by('-created_at')

    followers = Follow.objects.filter(
        following=request.user
    ).count()

    following = Follow.objects.filter(
        follower=request.user
    ).count()

    context = {
        "profile": profile,
        "posts": posts,
        "followers": followers,
        "following": following,
    }

    return render(request, "profile.html", context)


# ---------------- EDIT PROFILE ----------------

@login_required
def edit_profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profile Updated Successfully!")
            return redirect("profile")

    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "edit_profile.html",
        {"form": form}
    )


# ---------------- CREATE POST ----------------

@login_required
def create_post(request):

    if request.method == "POST":

        content = request.POST.get("content")
        image = request.FILES.get("image")

        Post.objects.create(
            user=request.user,
            content=content,
            image=image
        )

        messages.success(request, "Post Created Successfully!")

        return redirect("home")

    return render(request, "create_post.html")


# ---------------- LIKE / UNLIKE ----------------
@login_required
def like_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    like = Like.objects.filter(
        post=post,
        user=request.user
    )

    if like.exists():
        like.delete()
        messages.success(request, "Post Unliked")

    else:
        Like.objects.create(
            post=post,
            user=request.user
        )

        # Create notification
        if post.user != request.user:
            Notification.objects.create(
                user=post.user,
                message=f"{request.user.username} liked your post."
            )

        messages.success(request, "Post Liked")

    return redirect("home")


# ---------------- COMMENT ----------------
# ---------------- COMMENT ----------------
@login_required
def add_comment(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":

        content = request.POST.get("content")

        if content:

            Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )

            # Create notification
            if post.user != request.user:
                Notification.objects.create(
                    user=post.user,
                    message=f"{request.user.username} commented on your post."
                )

            messages.success(request, "Comment Added")

    return redirect("home")


# ---------------- FOLLOW / UNFOLLOW ----------------

# ---------------- FOLLOW / UNFOLLOW ----------------

@login_required
def follow_user(request, user_id):

    user_to_follow = get_object_or_404(User, id=user_id)

    if request.user != user_to_follow:

        follow = Follow.objects.filter(
            follower=request.user,
            following=user_to_follow
        )

        if follow.exists():

            follow.delete()
            messages.success(request, "User Unfollowed!")

        else:

            Follow.objects.create(
                follower=request.user,
                following=user_to_follow
            )

            Notification.objects.create(
                user=user_to_follow,
                message=f"{request.user.username} started following you."
            )

            messages.success(request, "User Followed!")

    return redirect("home")
@login_required
def delete_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if post.user == request.user:
        post.delete()
        messages.success(request, "Post deleted successfully!")

    return redirect("home")
@login_required
def edit_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        messages.error(request, "You cannot edit this post.")
        return redirect("home")

    if request.method == "POST":
        post.content = request.POST.get("content")

        if request.FILES.get("image"):
            post.image = request.FILES.get("image")

        post.save()

        messages.success(request, "Post updated successfully!")
        return redirect("home")

    return render(request, "edit_post.html", {"post": post})
@login_required
def search_users(request):

    query = request.GET.get("q")

    users = []

    if query:
        users = User.objects.filter(
            username__icontains=query
        )

    return render(
        request,
        "search.html",
        {
            "users": users,
            "query": query
        }
    )
@login_required
def user_profile(request, username):

    user = get_object_or_404(User, username=username)

    profile, created = Profile.objects.get_or_create(user=user)

    posts = Post.objects.filter(user=user).order_by('-created_at')

    followers = Follow.objects.filter(following=user).count()
    following = Follow.objects.filter(follower=user).count()
    is_following = Follow.objects.filter(
    follower=request.user,
    following=user
).exists()

    context = {
        "profile_user": user,
        "profile": profile,
        "posts": posts,
        "followers": followers,
        "following": following,
        "is_following": is_following,
    }

    return render(request, "user_profile.html", context)
@login_required
def notifications(request):

    notifications = request.user.notifications.order_by("-created_at")

    notifications.update(is_read=True)

    return render(
        request,
        "notifications.html",
        {
            "notifications": notifications
        }
    )
@login_required
def inbox(request):

    users = User.objects.exclude(id=request.user.id)

    return render(
        request,
        "inbox.html",
        {
            "users": users
        }
    )


@login_required
def chat(request, username):

    other_user = get_object_or_404(User, username=username)

    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by("created_at")

    if request.method == "POST":

        text = request.POST.get("message")

        if text:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                message=text
            )

        return redirect("chat", username=username)

    return render(
        request,
        "chat.html",
        {
            "other_user": other_user,
            "messages": messages
        }
    )
def unread_notification_count(request):
    if request.user.is_authenticated:
        return {
            "unread_notification_count": request.user.notifications.filter(
                is_read=False
            ).count()
        }

    return {
        "unread_notification_count": 0
    }