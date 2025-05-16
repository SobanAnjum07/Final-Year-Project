from django import forms
from .models import FacultyProfile, LectureContent, Subject

class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model = FacultyProfile
        fields = ['resume']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']

class LectureContentForm(forms.Form):
    # Subject options
    subject_choice = forms.ChoiceField(
        choices=[('existing', 'Choose existing subject'), ('new', 'Create new subject')],
        widget=forms.RadioSelect,
        initial='existing'
    )
    
    # Existing subject selection
    existing_subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),  # Will be set in __init__
        required=False
    )
    
    # New subject creation
    new_subject = forms.CharField(max_length=255, required=False)
    
    # Lecture content fields
    title = forms.CharField(max_length=255)
    
    lecture_type = forms.ChoiceField(
        choices=LectureContent.LECTURE_TYPE_CHOICES,
        initial=LectureContent.VIDEO
    )
    
    pdf = forms.FileField(required=False)
    video = forms.FileField(required=False)
    youtube_url = forms.URLField(required=False)
    
    def __init__(self, *args, faculty=None, **kwargs):
        super().__init__(*args, **kwargs)
        if faculty:
            # Filter subjects to show only those created by this faculty
            self.fields['existing_subject'].queryset = Subject.objects.filter(faculty=faculty)
    
    def clean(self):
        cleaned_data = super().clean()
        subject_choice = cleaned_data.get('subject_choice')
        
        if subject_choice == 'existing':
            # If choosing existing subject, validate it's selected
            if not cleaned_data.get('existing_subject'):
                self.add_error('existing_subject', 'Please select a subject')
        elif subject_choice == 'new':
            # If creating new subject, validate name is provided
            if not cleaned_data.get('new_subject'):
                self.add_error('new_subject', 'Please enter a subject name')
        
        # Validate proper files are filled based on lecture_type
        lecture_type = cleaned_data.get('lecture_type')
        
        # Clear validation for PDF file type
        if lecture_type == LectureContent.PDF:
            if not cleaned_data.get('pdf'):
                self.add_error('pdf', 'PDF file is required for PDF lecture type')
            elif cleaned_data.get('pdf'):
                file = cleaned_data.get('pdf')
                if not file.name.lower().endswith(('.pdf')):
                    self.add_error('pdf', 'Only PDF files are allowed for PDF lecture type')
        
        # Clear validation for Video file type
        elif lecture_type == LectureContent.VIDEO:
            if not cleaned_data.get('video'):
                self.add_error('video', 'Video file is required for Video lecture type')
            elif cleaned_data.get('video'):
                file = cleaned_data.get('video')
                if not file.name.lower().endswith(('.mp4', '.mov', '.avi', '.wmv', '.mkv')):
                    self.add_error('video', 'Only video files (mp4, mov, avi, wmv, mkv) are allowed for Video lecture type')
        
        # Clear validation for YouTube URL
        elif lecture_type == LectureContent.YOUTUBE:
            if not cleaned_data.get('youtube_url'):
                self.add_error('youtube_url', 'YouTube URL is required for YouTube lecture type')
            
        return cleaned_data