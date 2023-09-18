from django import forms

from .models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ("text", "tag", "image", "name", "ingredients", "cooking_time")
        label = {
	        "text": "Опишите рецепт", "tag": "Добавьте теги",
	        "ingredients": "Добавьте ингредиенты",
	        "cooking_time": "Добавьте время приготовления"
        }
        help_text = {
            "text": "Самое время печатать буквы",
            "tag": "Нужно выбрать теги",
        }

    def clean_text(self):
        text = self.cleaned_data["text"]
        if text == " ":
            raise forms.ValidationError("Рецепт не может быть пустым")
        return text
