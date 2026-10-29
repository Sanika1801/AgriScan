from django.urls import path
from . import views

urlpatterns = [
    # Expert Consultation URLs
    path('experts/', views.expert_list, name='expert_list'),
    path('experts/book/<int:expert_id>/', views.book_consultation, name='book_consultation'),
    path('expert-dashboard/', views.agronomist_dashboard, name='agronomist_dashboard'),
    path('expert-dashboard/review/<int:pk>/', views.review_case, name='review_case'),
    path('expert-dashboard/update/<int:consultation_id>/<str:status>/', views.update_consultation, name='update_consultation'),
    
    # Community Forum URLs (ADD THESE)
    path('forum/', views.forum_list, name='forum_list'),
    path('forum/new/', views.create_post, name='create_post'),
    path('forum/<int:post_id>/', views.post_detail, name='post_detail'),
    path('expert-dashboard/delete/<int:pk>/', views.delete_triage_case, name='delete_triage_case'),
]