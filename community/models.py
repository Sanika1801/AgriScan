from django.db import models
from accounts.models import User

class ForumPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class ForumComment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class ExpertConsultation(models.Model):
    STATUS = [('pending', 'Pending'), ('approved', 'Approved'), ('completed', 'Completed')]
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations_as_farmer')
    agronomist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations_as_expert')
    issue_description = models.TextField()
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS, default='pending')