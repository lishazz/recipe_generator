from django import forms

class IngredientForm(forms.Form):
    ingredients = forms.CharField(
        label="Enter Ingredients",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g., tomato, cheese, basil"
        }),
        required=True
    )