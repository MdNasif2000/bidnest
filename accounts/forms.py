from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, StudentProfile, LandlordProfile, Review

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    university = forms.CharField(max_length=200, required=True)
    terms = forms.BooleanField(required=True, error_messages={'required': 'You must agree to the terms and conditions'})
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make first_name and last_name required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                university=self.cleaned_data['university'],
                course='',  # Will be filled later in profile
                year_of_study=1,  # Default value
                student_id=''  # Will be filled later in profile
            )
        return user


class LandlordRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    company_name = forms.CharField(max_length=200, required=False)
    address = forms.CharField(widget=forms.Textarea, required=True)
    city = forms.CharField(max_length=100, required=True)
    postcode = forms.CharField(max_length=10, required=True)
    terms = forms.BooleanField(required=True, error_messages={'required': 'You must agree to the terms and conditions'})
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make first_name and last_name required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'landlord'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            LandlordProfile.objects.create(
                user=user,
                company_name=self.cleaned_data.get('company_name', ''),
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                postcode=self.cleaned_data['postcode']
            )
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['university', 'course', 'year_of_study', 'proof_of_study', 'id_document', 
                  'emergency_contact_name', 'emergency_contact_phone', 'bio']


class LandlordProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = LandlordProfile
        fields = ['company_name', 'business_registration', 'address', 'city', 'postcode', 
                  'id_document', 'proof_of_ownership', 'bio']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
        }
