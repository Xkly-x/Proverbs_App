from django.contrib import admin
from .models import Category, Proverb, Profile, Achievement, Comment

@admin.register(Proverb)
class ProverbAdmin(admin.ModelAdmin):
    list_display = ('text', 'status', 'author', 'likes_count', 'created_at', 'is_featured')
    list_filter = ('status', 'difficulty', 'is_featured', 'categories')
    search_fields = ('text', 'meaning')
    filter_horizontal = ('categories', 'likes')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'proverb', 'created_at')
    search_fields = ('text', 'user__username', 'proverb__text')

admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(Achievement)