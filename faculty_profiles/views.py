from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FacultyProfile, LectureContent, Subject
from .forms import FacultyProfileForm, LectureContentForm, SubjectForm


@login_required
def faculty_dashboard(request):
    # Get or create the faculty profile for the current user.
    faculty_profile, created = FacultyProfile.objects.get_or_create(user=request.user)
    
    # Process the FacultyProfile form for resume updates.
    if request.method == "POST":
        profile_form = FacultyProfileForm(request.POST, request.FILES, instance=faculty_profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('faculty_dashboard')
    else:
        profile_form = FacultyProfileForm(instance=faculty_profile)
    
    resume_link = faculty_profile.resume.url if faculty_profile.resume else None
    
    # Get all subjects for this faculty
    subjects = Subject.objects.filter(faculty=faculty_profile)
    
    # Group lectures by subject.
    lectures_by_subject = {}
    for subject in subjects:
        lectures = LectureContent.objects.filter(subject=subject)
        if lectures.exists():
            lectures_by_subject[subject] = lectures
    
    return render(request, "faculty_profiles/dashboard.html", {
        "profile_form": profile_form,
        "resume_link": resume_link,
        "lectures_by_subject": lectures_by_subject,
    })


@login_required
def upload_lecture(request):
    faculty_profile = get_object_or_404(FacultyProfile, user=request.user)
    
    if request.method == "POST":
        form = LectureContentForm(request.POST, request.FILES, faculty=faculty_profile)
        
        if form.is_valid():
            # Get or create the subject
            subject_choice = form.cleaned_data['subject_choice']
            
            if subject_choice == 'existing':
                subject = form.cleaned_data['existing_subject']
            else:  # new subject
                subject_name = form.cleaned_data['new_subject']
                subject, created = Subject.objects.get_or_create(
                    name=subject_name,
                    faculty=faculty_profile
                )
            
            # Create the lecture content
            lecture = LectureContent(
                faculty=faculty_profile,
                subject=subject,
                title=form.cleaned_data['title'],
                lecture_type=form.cleaned_data['lecture_type']
            )
            
            # Set the appropriate file based on lecture type
            if lecture.lecture_type == LectureContent.PDF:
                lecture.pdf = form.cleaned_data['pdf']
            elif lecture.lecture_type == LectureContent.VIDEO:
                lecture.video = form.cleaned_data['video']
            elif lecture.lecture_type == LectureContent.YOUTUBE:
                lecture.youtube_url = form.cleaned_data['youtube_url']
            
            lecture.save()
            messages.success(request, "Lecture uploaded successfully!")
            return redirect('faculty_dashboard')
    else:
        form = LectureContentForm(faculty=faculty_profile)

    return render(request, "faculty_profiles/upload_lecture.html", {"form": form})

@login_required
def edit_lecture(request, lecture_id):
    # Ensure only the owner can edit the lecture
    lecture = get_object_or_404(LectureContent, id=lecture_id, faculty__user=request.user)
    faculty_profile = lecture.faculty
    
    if request.method == "POST":
        form = LectureContentForm(request.POST, request.FILES, faculty=faculty_profile)
        if form.is_valid():
            # Get or create the subject
            subject_choice = form.cleaned_data['subject_choice']
            
            if subject_choice == 'existing':
                subject = form.cleaned_data['existing_subject']
            else:  # new subject
                subject_name = form.cleaned_data['new_subject']
                subject, created = Subject.objects.get_or_create(
                    name=subject_name,
                    faculty=faculty_profile
                )
            
            # Update the lecture
            lecture.subject = subject
            lecture.title = form.cleaned_data['title']
            
            # Check if lecture type has changed
            old_lecture_type = lecture.lecture_type
            new_lecture_type = form.cleaned_data['lecture_type']
            
            lecture.lecture_type = new_lecture_type
            
            # Update the appropriate file based on lecture type
            if new_lecture_type == LectureContent.PDF:
                if form.cleaned_data['pdf']:
                    # If a new PDF was uploaded, use it
                    lecture.pdf = form.cleaned_data['pdf']
                # Clear other file fields
                lecture.video = None
                lecture.youtube_url = None
                
            elif new_lecture_type == LectureContent.VIDEO:
                if form.cleaned_data['video']:
                    # If a new video was uploaded, use it
                    lecture.video = form.cleaned_data['video']
                # Clear other file fields
                lecture.pdf = None
                lecture.youtube_url = None
                
            elif new_lecture_type == LectureContent.YOUTUBE:
                if form.cleaned_data['youtube_url']:
                    # Update YouTube URL
                    lecture.youtube_url = form.cleaned_data['youtube_url']
                # Clear other file fields
                lecture.pdf = None
                lecture.video = None
            
            lecture.save()
            messages.success(request, "Lecture updated successfully!")
            return redirect('faculty_dashboard')
    else:
        # Pre-populate form with lecture data
        initial_data = {
            'subject_choice': 'existing',
            'existing_subject': lecture.subject,
            'title': lecture.title,
            'lecture_type': lecture.lecture_type,
            'youtube_url': lecture.youtube_url
        }
        form = LectureContentForm(initial=initial_data, faculty=faculty_profile)

    return render(request, "faculty_profiles/edit_lecture.html", {"form": form, "lecture": lecture})

@login_required
def delete_lecture(request, lecture_id):
    lecture = get_object_or_404(LectureContent, id=lecture_id, faculty__user=request.user)
    if request.method == "POST":
        lecture.delete()
        messages.success(request, "Lecture deleted successfully!")
        return redirect('faculty_dashboard')
    return render(request, "faculty_profiles/confirm_delete.html", {"lecture": lecture})


@login_required
def create_faculty_profile(request):
    # Check if the profile already exists
    if FacultyProfile.objects.filter(user=request.user).exists():
        return redirect('faculty_dashboard')
    
    if request.method == "POST":
        form = FacultyProfileForm(request.POST, request.FILES)
        if form.is_valid():
            faculty_profile = form.save(commit=False)
            faculty_profile.user = request.user
            faculty_profile.save()
            messages.success(request, "Faculty profile created successfully!")
            return redirect('faculty_dashboard')
    else:
        form = FacultyProfileForm()
        
    return render(request, "faculty_profiles/create_faculty_profile.html", {"form": form})

@login_required
def manage_subjects(request):
    faculty_profile = get_object_or_404(FacultyProfile, user=request.user)
    subjects = Subject.objects.filter(faculty=faculty_profile)
    
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.faculty = faculty_profile
            subject.save()
            messages.success(request, "Subject created successfully!")
            return redirect('manage_subjects')
    else:
        form = SubjectForm()
        
    return render(request, "faculty_profiles/manage_subjects.html", {
        "form": form,
        "subjects": subjects
    })