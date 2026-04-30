from django import forms
from .models import Bid

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount', 'message']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': 'Enter your bid amount'}),
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional message to landlord...'}),
        }
        labels = {
            'amount': 'Bid Amount (£)',
            'message': 'Message (Optional)',
        }


class CounterOfferForm(forms.Form):
    counter_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Enter counter offer amount'}),
        label='Counter Offer Amount (£)'
    )
    counter_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional message to student...'}),
        label='Message (Optional)'
    )
