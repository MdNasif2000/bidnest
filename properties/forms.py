from django import forms
from .models import Property, PropertyImage, AccommodationRequest

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        exclude = ['landlord', 'current_bid', 'views_count', 'is_active', 'created_at', 'updated_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'available_from': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'available_until': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'bedrooms': forms.NumberInput(attrs={'min': 0}),
            'bathrooms': forms.NumberInput(attrs={'min': 0}),
            'square_feet': forms.NumberInput(attrs={'min': 0}),
            'starting_bid': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'rent_per_month': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'deposit': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set input formats for date fields
        self.fields['available_from'].input_formats = ['%Y-%m-%d']
        self.fields['available_until'].input_formats = ['%Y-%m-%d']


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption', 'is_primary']


class PropertySearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search properties...'}))
    city = forms.CharField(required=False)
    campus = forms.CharField(required=False)
    property_type = forms.ChoiceField(choices=[('', 'All Types')] + list(Property.PROPERTY_TYPE_CHOICES), required=False)
    min_price = forms.DecimalField(required=False, min_value=0)
    max_price = forms.DecimalField(required=False, min_value=0)
    bedrooms = forms.IntegerField(required=False, min_value=1)
    academic_year = forms.CharField(required=False)
    furnishing = forms.ChoiceField(choices=[('', 'Any')] + list(Property.FURNISHING_CHOICES), required=False)
    bills_included = forms.BooleanField(required=False)
    wifi = forms.BooleanField(required=False)
    parking = forms.BooleanField(required=False)


class AccommodationRequestForm(forms.ModelForm):
    # Multi-select furnishing preferences
    furnishing_furnished = forms.BooleanField(required=False, label='Furnished')
    furnishing_unfurnished = forms.BooleanField(required=False, label='Unfurnished')
    furnishing_part_furnished = forms.BooleanField(required=False, label='Part Furnished')
    
    class Meta:
        model = AccommodationRequest
        exclude = ['student', 'created_at', 'updated_at', 'is_active', 'furnishing_preference']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Tell landlords what you\'re looking for...'}),
            'additional_requirements': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any other requirements or preferences...'}),
            'move_in_date': forms.DateInput(attrs={'type': 'date'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Looking for a 2-bed flat near City Campus'}),
            'preferred_location': forms.TextInput(attrs={'placeholder': 'e.g., City Centre, Fallowfield'}),
            'campus': forms.TextInput(attrs={'placeholder': 'e.g., City Campus'}),
            'academic_year': forms.TextInput(attrs={'placeholder': 'e.g., 2025/2026'}),
            'min_budget': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'placeholder': 'Min £'}),
            'max_budget': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'placeholder': 'Max £'}),
            'bedrooms_needed': forms.NumberInput(attrs={'min': 0, 'placeholder': 'Number of bedrooms'}),
        }
        labels = {
            'interested_in_buddy_up': 'I/we are also interested in Buddying up',
        }
        help_texts = {
            'interested_in_buddy_up': 'Tick this if you might like to Buddy Up with other room seekers to find a whole flat or house together and start a brand new flat/house share.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate furnishing checkboxes if editing
        if self.instance and self.instance.furnishing_preference:
            prefs = self.instance.furnishing_preference.split(',')
            if 'furnished' in prefs:
                self.fields['furnishing_furnished'].initial = True
            if 'unfurnished' in prefs:
                self.fields['furnishing_unfurnished'].initial = True
            if 'part_furnished' in prefs:
                self.fields['furnishing_part_furnished'].initial = True
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Combine furnishing preferences
        prefs = []
        if self.cleaned_data.get('furnishing_furnished'):
            prefs.append('furnished')
        if self.cleaned_data.get('furnishing_unfurnished'):
            prefs.append('unfurnished')
        if self.cleaned_data.get('furnishing_part_furnished'):
            prefs.append('part_furnished')
        instance.furnishing_preference = ','.join(prefs)
        if commit:
            instance.save()
        return instance
