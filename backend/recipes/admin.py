from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count

from users.models import Follow
from .models import Ingredient, Tag, Recipe, Favorite

# в админке не хватает ток общее число сохраненок рецептов вывести
User = get_user_model

admin.site.register(Tag)
admin.site.register(Follow)
admin.site.register(Favorite)

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
# 	list_filter = ['email', 'name']

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
	list_display = ['name', 'author']
	list_filter = ('author', 'tags__name', 'name')
	search_fields = ('name', 'author__username')
	ordering = ('-pub_date',)

# def get_queryset(self, request):
# 		queryset = super().get_queryset(request)
# 		return queryset.annotate(favorite_count=Count('favored_by'))
#
# 	@staticmethod
# 	def get_favorites_count(obj):
# 		return obj.favorite_count


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
	list_display = ['name', 'measurement_unit']
	search_fields = ('^name',)
