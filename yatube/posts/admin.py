from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Перчеслиям поля, которые должны отображиться
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    # добовляем возможность для поиска по группам
    list_editable = ('group',)
    search_fields = ('text',)
    # добавляем возможность филтрации по дате
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'post', 'created')
    list_editable = ('post', 'author')
    list_filter = ('created',)
    search_fields = ('text', 'author')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user__pk',)
