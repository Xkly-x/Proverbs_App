from django.contrib import admin
from .models import Category, Proverb, Profile, Achievement

admin.site.register(Category)
admin.site.register(Proverb)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_score', 'current_streak', 'rank']
    list_filter = ['last_activity_date']
    search_fields = ['user__username']

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'description']