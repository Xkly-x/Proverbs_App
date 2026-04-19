from django.contrib.auth.models import User
from django.db import models
from datetime import date, timedelta


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Proverb(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Одобрено'),
        ('pending', 'На модерации'),
        ('rejected', 'Отклонено'),
    ]
    text = models.CharField(max_length=500, verbose_name="Текст пословицы")
    meaning = models.TextField(verbose_name="Смысл/Толкование")
    categories = models.ManyToManyField(Category, related_name="proverbs", verbose_name="Категории", blank=True)
    DIFFICULTY_CHOICES = [
        (1, 'Легко'),
        (2, 'Средне'),
        (3, 'Сложно'),
    ]
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=1, verbose_name="Сложность")
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_proverbs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    is_featured = models.BooleanField(default=False, verbose_name="Пословица дня")
    likes = models.ManyToManyField(User, blank=True, related_name='liked_proverbs')

    def __str__(self):
        return self.text

    @property
    def likes_count(self):
        return self.likes.count()

    class Meta:
        verbose_name = "Пословица"
        verbose_name_plural = "Пословицы"
        ordering = ['-created_at']


class Comment(models.Model):
    proverb = models.ForeignKey(Proverb, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}"


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="🏆")

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/default.png')
    total_score = models.IntegerField(default=0)
    completed_quizzes = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    achievements = models.ManyToManyField(Achievement, blank=True)

    @property
    def rank(self):
        if self.total_score >= 100:
            return "Мастер народной мудрости 🧙‍♂️"
        elif self.total_score >= 50:
            return "Знаток 🎓"
        elif self.total_score >= 10:
            return "Ученик 📚"
        else:
            return "Новичок 🌱"

    def update_streak(self):
        today = date.today()
        if self.last_activity_date == today:
            pass
        elif self.last_activity_date == today - timedelta(days=1):
            self.current_streak += 1
        else:
            self.current_streak = 1
        self.last_activity_date = today
        self.save()

    def __str__(self):
        return f"Профиль {self.user.username}"

    @property
    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return "/static/images/default-user.png"