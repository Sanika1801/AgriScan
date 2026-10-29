from .models import ForumPost, ForumComment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import User, AgronomistProfile
from .models import ExpertConsultation
from detector.models import PredictionLog

@login_required
def expert_list(request):
    if request.user.role != 'farmer':
        return redirect('home')
    
    # Get all users who are agronomists and have a profile
    experts = AgronomistProfile.objects.select_related('user').all()
    return render(request, 'community/expert_list.html', {'experts': experts})

@login_required
def book_consultation(request, expert_id):
    if request.user.role != 'farmer':
        return redirect('home')
        
    expert_profile = get_object_or_404(AgronomistProfile, user__id=expert_id)
    
    if request.method == 'POST':
        issue = request.POST.get('issue_description')
        date_str = request.POST.get('scheduled_time')
        
        # Save the consultation to the database
        ExpertConsultation.objects.create(
            farmer=request.user,
            agronomist=expert_profile.user,
            issue_description=issue,
            scheduled_time=date_str,
            status='pending'
        )
        messages.success(request, f"✅ Consultation requested with Dr. {expert_profile.user.username}!")
        return redirect('home')
        
    return render(request, 'community/book_consultation.html', {'expert': expert_profile})

@login_required
def agronomist_dashboard(request):
    if request.user.role != 'agronomist':
        return redirect('home')
        
    consultations = ExpertConsultation.objects.filter(agronomist=request.user).order_by('-id')
    return render(request, 'community/agronomist_dashboard.html', {'consultations': consultations})

@login_required
def update_consultation(request, consultation_id, status):
    if request.user.role != 'agronomist':
        return redirect('home')
        
    consultation = get_object_or_404(ExpertConsultation, id=consultation_id, agronomist=request.user)
    if status in ['approved', 'completed']:
        consultation.status = status
        consultation.save()
        messages.success(request, f"Consultation marked as {status}.")
    return redirect('agronomist_dashboard')

def forum_list(request):
    posts = ForumPost.objects.all().order_by('-created_at')
    return render(request, 'community/forum_list.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        ForumPost.objects.create(author=request.user, title=title, content=content)
        messages.success(request, "Post created successfully!")
        return redirect('forum_list')
    return render(request, 'community/create_post.html')

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    comments = post.comments.all().order_by('created_at')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        ForumComment.objects.create(post=post, author=request.user, content=content)
        return redirect('post_detail', post_id=post.id)
        
    return render(request, 'community/post_detail.html', {'post': post, 'comments': comments})


@login_required
def agronomist_dashboard(request):
    if request.user.role != 'agronomist':
        return redirect('dashboard')
        
    # 1. Case Escalation Inbox (Confidence < 70%)
    escalated_cases = PredictionLog.objects.filter(confidence__lt=70).order_by('-date_uploaded')
    
    # 2. Filtering Logic
    crop_filter = request.GET.get('crop')
    if crop_filter:
        escalated_cases = escalated_cases.filter(predicted_disease__icontains=crop_filter)
        
    # Existing Video Consultations
    consultations = ExpertConsultation.objects.filter(agronomist=request.user).order_by('-id')
    
    context = {
        'escalated_cases': escalated_cases,
        'consultations': consultations,
        'total_pending': escalated_cases.filter(review_status='pending').count(),
        'total_verified': escalated_cases.filter(review_status='verified').count(),
    }
    return render(request, 'community/agronomist_dashboard.html', context)


@login_required
def review_case(request, pk):
    if request.user.role != 'agronomist':
        return redirect('dashboard')
        
    case = get_object_or_404(PredictionLog, id=pk)
    
    if request.method == 'POST':
        # Digital Prescription Pad Submission
        case.expert_diagnosis = request.POST.get('expert_diagnosis')
        case.organic_cure = request.POST.get('organic_cure')
        case.chemical_cure = request.POST.get('chemical_cure')
        case.prevention_practice = request.POST.get('prevention_practice')
        case.review_status = 'verified'
        case.save()
        
        messages.success(request, "✅ Prescription saved successfully!")
        return redirect('agronomist_dashboard')

    return render(request, 'community/review_case.html', {'case': case})

@login_required
def delete_triage_case(request, pk):
    if request.user.role != 'agronomist':
        return redirect('dashboard')
    
    from detector.models import PredictionLog
    case = get_object_or_404(PredictionLog, id=pk)
    case.delete()
    
    from django.contrib import messages
    messages.success(request, "🗑️ Case removed from Triage Inbox.")
    return redirect('agronomist_dashboard')