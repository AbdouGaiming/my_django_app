from django.contrib import admin
from .models import Resource, ResourceLink


class ResourceLinkInline(admin.TabularInline):
    model = ResourceLink
    extra = 1


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'language', 'difficulty', 'quality_score', 'is_free', 'is_active']
    list_filter = ['resource_type', 'language', 'difficulty', 'is_free', 'is_active', 'algeria_relevant']
    search_fields = ['title', 'title_ar', 'description', 'author', 'channel_name']
    inlines = [ResourceLinkInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'title_ar', 'description', 'description_ar', 'resource_type')
        }),
        ('Provider', {
            'fields': ('provider', 'author', 'channel_name')
        }),
        ('YouTube Info', {
            'fields': ('youtube_video_id', 'youtube_playlist_id', 'youtube_channel_id'),
            'classes': ('collapse',)
        }),
        ('Book Info', {
            'fields': ('isbn', 'publisher', 'publication_year', 'page_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('language', 'difficulty', 'duration_minutes', 'video_count', 'tags', 'skills_covered')
        }),
        ('Quality', {
            'fields': ('quality_score', 'upvotes', 'downvotes', 'view_count')
        }),
        ('Status', {
            'fields': ('is_free', 'is_active', 'is_arabic_friendly', 'has_subtitles', 'algeria_relevant')
        }),
    )


@admin.register(ResourceLink)
class ResourceLinkAdmin(admin.ModelAdmin):
    list_display = ['resource', 'url', 'is_primary', 'is_working']
    list_filter = ['is_primary', 'is_working']
    search_fields = ['url', 'resource__title']
