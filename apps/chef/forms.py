from django import forms
from django.forms import formset_factory
from apps.common.models import Recipe, RecipeIngredient,User

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["title", "category", "description", "instruction", "cook_time", "recipe_image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control "}),
            "category": forms.Select(attrs={"class": "form-control form-select "}),
            "description": forms.Textarea(attrs={"class": "form-control ", "rows": 2}),
            "instruction": forms.Textarea(attrs={"class": "form-control ", "rows": 3}),
            "cook_time": forms.NumberInput(attrs={"class": "form-control "}),
            "recipe_image": forms.FileInput(attrs={"class": "form-control "}),
        }

class IngredientForm(forms.Form):
    ingredient_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
    ingredient_quantity = forms.FloatField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}))

IngredientFormSet = formset_factory(IngredientForm, extra=3)  # Default 3 ingredient fields


class ChefSettingsForm(forms.ModelForm):
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

