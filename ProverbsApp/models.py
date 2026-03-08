from django.contrib.auth.models import User
from django.db import models
from datetime import date, timedelta


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Proverb(models.Model):
    text = models.CharField(max_length=255)
    meaning = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='proverbs')

    def __str__(self):
        return self.text


# модель для Ачивок
class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="🏆")

    def __str__(self):
        return self.name


# Профиль
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/default.png')
    total_score = models.IntegerField(default=0)
    completed_quizzes = models.IntegerField(default=0)

    # Ударный режим (Streak)
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