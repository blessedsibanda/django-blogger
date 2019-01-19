from django.contrib import admin

from .models import Article, Profile

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'publish', 'created', 'author']
    list_filter = ('author', 'title',)
    list_editable = ('publish',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'github', 'website']