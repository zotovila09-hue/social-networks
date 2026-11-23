from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

def validate_file_size(file):
    if file.size > 500 * 1024 * 1024:
        raise ValidationError("Файл слишком большой! Максимальный размер 5 МБ.")

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", verbose_name="Автор")
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Текст поста")
    code = models.TextField(blank=True, verbose_name="Код")
    launguage = models.CharField(max_length=30, default="python", verbose_name="Язык программирования")
    attached_file = models.FileField(
        upload_to='post_files/%Y/%m/',
        blank=True,
        null=True,
        validators=[
            validate_file_size,
            FileExtensionValidator(allowed_extensions=['py', 'js', 'ts', 'cpp', 'sql', 'json', 'txt', 'zip', 'png', 'jpg'])
        ],
        verbose_name="Прикрепленный файл"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    def __str__(self):
        return f"{self.author.username} - {self.title}"

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ['-created_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="Пост")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", verbose_name="Автор")
    content = models.TextField(verbose_name="Текст коммента")
    code = models.TextField(blank=True, verbose_name="код")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.author.username} к 'self.post.title'"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages", verbose_name="Отправитель")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", verbose_name="Получатель")
    text = models.TextField(verbose_name="Текст сообщения")
    code = models.TextField(blank=True, verbose_name="Код")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время отправки")

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.text[:20]}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['created_at']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="Пользователи")
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True, verbose_name="Аватарка")
    bio = models.TextField(max_length=255, blank=True, verbose_name="О себе")
    specialization = models.CharField(max_length=100, blank=True, default="Не выбранно", verbose_name="Специализация")
    github = models.URLField(max_length=200, blank=True, verbose_name="Github")
    def __str__(self):
        return f"Профиль {self.user.username}"
    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

