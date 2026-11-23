from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Post, Comment, Message, Profile

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = UserCreationForm()
    return render(request, 'network/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('feed')
    else:
        form = AuthenticationForm()
    return render(request, 'network/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('feed')

def feed(request):
    if request.method == 'POST' and request.user.is_authenticated:
        title = request.POST.get('title')
        content = request.POST.get('content')
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python')
        attached_file = request.FILES.get('attached_file')
        if title and content:
            post = Post(
                author=request.user,
                title=title,
                content=content,
                code=code,
                launguage=language,
                attached_file=attached_file
            )
            try:
                post.full_clean()
                post.save()
                return redirect('feed')
            except ValidationError as e:
                posts = Post.objects.all()
                error_msg = e.messages[0] if e.messages else "Ошибка валидации файла."
                return render(request, 'network/feed.html', {'posts': posts, 'error': error_msg})
    posts = Post.objects.all()
    return render(request, 'network/feed.html', {'posts': posts})

def add_comment(request, post_id):
    if request.method == 'POST' and request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content')
        code = request.POST.get('code', '')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                code=code
            )
    return redirect(f"/#post-{post_id}")

def profile(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        if not request.user.is_authenticated:
            return redirect('login')
        profile_user = request.user
    profile, _ = Profile.objects.get_or_create(user=profile_user)
    user_posts = Post.objects.filter(author=profile_user)
    user_comments_count = Comment.objects.filter(author=profile_user).count()
    is_own_profile = (request.user.is_authenticated and request.user == profile_user)
    return render(request, 'network/profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'user_posts': user_posts,
        'user_comments_count': user_comments_count,
        'is_own_profile': is_own_profile
    })

def chat(request, user_id=None):
    if not request.user.is_authenticated:
        return redirect('login')

    other_users = User.objects.exclude(id=request.user.id)
    recipient = None
    messages_list = []

    if user_id:
        recipient = get_object_or_404(User, id=user_id)
        if request.method == 'POST':
            text = request.POST.get('text')
            code = request.POST.get('code', '')
            if text:
                Message.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    text=text,
                    code=code
                )
                return redirect('chat_with_user', user_id=user_id)

        messages_list = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient=recipient)) |
            (Q(sender=recipient) & Q(recipient=request.user))
        ).order_by('created_at')

    return render(request, 'network/chat.html', {
        'other_users': other_users,
        'recipient': recipient,
        'messages_list': messages_list
    })

def delete_post(request, post_id):
    if request.method == 'POST' and request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        if post.author == request.user:
            post.delete()
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.specialization = request.POST.get('specialization', '')
        profile.bio = request.POST.get('bio', '')
        profile.github = request.POST.get('github', '')
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES.get('avatar')
        profile.save()
        return redirect('profile')
    return render(request, 'network/edit_profile.html', {'profile': profile})

def delete_comment(request, comment_id):
    if request.method == 'POST' and request.user.is_authenticated:
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.author == request.user:
            comment.delete()
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

def delete_profile(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        logout(request)
        user.delete()
    return redirect('feed')
