from django import forms
from apps.common.models import Recipe  

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'category', 'description', 'instruction', 'cook_time', 'recipe_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'category': forms.Select(attrs={'class': 'form-select', 'required': True}, choices=Recipe.CATEGORY_CHOICES),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
            'instruction': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'required': True}),
            'cook_time': forms.NumberInput(attrs={'class': 'form-control', 'required': True}),
            'recipe_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
