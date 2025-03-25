from django import forms
from django.forms import formset_factory
from apps.common.models import Recipe, RecipeIngredient

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




