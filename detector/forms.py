from django import forms
from .models import CropCycle

class CropCycleForm(forms.ModelForm):
    class Meta:
        model = CropCycle
        fields = ['crop', 'sowing_date']
        widgets = {
            'sowing_date': forms.DateInput(attrs={
                'type': 'date', 
                'style': 'width: 100%; padding: 12px; border: 1px solid #D1D5DB; border-radius: 8px; font-family: Inter; box-sizing: border-box;'
            }),
            'crop': forms.Select(attrs={
                'style': 'width: 100%; padding: 12px; border: 1px solid #D1D5DB; border-radius: 8px; font-family: Inter; box-sizing: border-box;'
            })
        }