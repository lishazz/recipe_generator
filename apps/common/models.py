from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class User(AbstractUser):
    ROLES = (
        ('generaluser', 'General User'),  # Fixed typo
        ('chef', 'Chef')
    )
    role = models.CharField(max_length=20, choices=ROLES, default='default')
    registration_date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=True)
    

    # Explicit related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Custom related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Custom related_name
        blank=True
    )

    def __str__(self):  # Fixed method name
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Ingredient(models.Model):
    CATEGORY_CHOICES = (
        ('vegetable', 'Vegetable'),
        ('fruit', 'Fruit'),
        ('meat', 'Meat'),
        ('dairy', 'Dairy'),
        ('grain', 'Grain'),
        ('other', 'Other'),
    )
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    calories_per_100g = models.FloatField(validators=[MinValueValidator(0)],null='false')
    protein_per_100g = models.FloatField(validators=[MinValueValidator(0)],null='false')
    carbs_per_100g = models.FloatField(validators=[MinValueValidator(0)],null='false')
    fats_per_100g = models.FloatField(validators=[MinValueValidator(0)],null='false')

    def __str__(self):
        return f"Ingredient: {self.name} ({self.category})"


class Recipe(models.Model):
    CATEGORY_CHOICES = (
        ('veg', 'Vegetarian'),
        ('nonveg', 'Non-Vegetarian'),

    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    instruction = models.TextField()
    cook_time = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="Time in minutes")
    category = models.CharField(max_length=20,choices=CATEGORY_CHOICES, default='veg')
    recipe_image = models.ImageField(upload_to='recipe_images/', null=True, blank=True )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recipe: {self.title} ({self.description})"
    

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(help_text="Quantity in standard units")

    def __str__(self):
        return f"{self.quantity} of {self.ingredient.name} in {self.recipe.title}"
    
    
class GenerateRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="generated_recipes")
    user_input_ingredients = models.TextField(help_text="Comma-separated list of ingredients")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Generated Recipe: {self.recipe.title if self.recipe else 'N/A'} by {self.user.username}"


class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_ratings")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'user'], name='unique_user_recipe_rating')
        ]
    def __str__(self):
        return f"{self.rating} stars for {self.recipe.title} by {self.user.username}"
    

class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_recipes")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')  # Ensure a user cannot favorite the same recipe multiple times

    def __str__(self):
        return f"{self.user.username} favorited {self.recipe.title}"

class ReviewReply(models.Model):
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='replies')
    chef = models.ForeignKey(User, on_delete=models.CASCADE)
    reply_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class ChefRating(models.Model):
    chef = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chef', 'user')
        ordering = ['-created_at']