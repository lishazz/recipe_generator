from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from apps.common.models import User

class IngredientForm(forms.Form):
    ingredients = forms.CharField(
        label="Enter Ingredients",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g., tomato, cheese, basil"
        }),
        required=True
    )

class UserSettingsForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['current_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['confirm_password'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and new_password != confirm_password:
            raise forms.ValidationError("New passwords don't match")
        return cleaned_data