from django.contrib import admin
from .models import ForumPost, ForumComment, ExpertConsultation

@admin.register(ExpertConsultation)
class ExpertConsultationAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'agronomist', 'scheduled_time', 'status')
    list_filter = ('status',)

admin.site.register(ForumPost)
admin.site.register(ForumComment)