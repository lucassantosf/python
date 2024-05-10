from django.urls import reverse, resolve
from recipes import views
from .test_recipe_base import RecipeTestBase

class RecipeCategoryViewTest(RecipeTestBase):
    def test_recipe_category_views_function_is_correct(self):
        view = resolve(
            reverse('recipes:category', kwargs={'category_id':1})
        )
        self.assertIs(view.func.view_class, views.RecipeListViewCategory)

    def test_recipe_category_view_returns_404_if_no_recipes_found(self):
        response = self.client.get(
            reverse('recipes:category', kwargs={'category_id':100011})
        )
        self.assertEqual(response.status_code, 404)

    def test_recipe_category_template_loads_recipes(self):
        needed_title = 'This is a category test'
        self.make_recipe(title=needed_title)

        response = self.client.get(reverse('recipes:category',args=(1,)))
        content = response.content.decode('utf-8')
        response_context_recipes = response.context['recipes']

        self.assertIn(needed_title,content) 

    def test_recipe_category_template_does_not_load_recipes_not_published(self):
        """Test recipe is_published False doesnt show"""
        recipe = self.make_recipe(is_published=False)

        response = self.client.get(reverse('recipes:recipe',kwargs={'pk':recipe.category.id}))

        self.assertEqual(response.status_code,404)