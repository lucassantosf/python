from django.test import TestCase
from recipes.models import Category, Recipe, User

class RecipeMixing:
    def make_category(self, name = 'Category'):
        return Category.objects.create(name=name)

    def make_author(self, first_name='user',last_name='sil',username='username',password='123456',email='username@gmail.com'):
        return User.objects.create(first_name=first_name,last_name=last_name,username=username,password=password,email=email)

    def make_recipe(self, author_data=None, category_data=None,title = 'Recipe title',description = 'Recipe description',slug = 'Recipe-slug',preparation_time = 10,preparation_time_unit = 'Recipe minutos',servings = 5,servings_unit = 'Porções',preparation_steps = 'Recipe preparation_steps',preparation_steps_is_html = False,is_published = True):
        if author_data is None:
            author_data = {}

        if category_data is None:
            category_data = {}

        return Recipe.objects.create(
            author = self.make_author(**author_data),
            category = self.make_category(**category_data),
            title = title,
            description = description,
            slug = slug,
            preparation_time = preparation_time ,
            preparation_time_unit = preparation_time_unit ,
            servings = servings ,
            servings_unit = servings_unit ,
            preparation_steps = preparation_steps ,
            preparation_steps_is_html = preparation_steps_is_html ,
            is_published = is_published , 
        )

    def make_recipe_in_batch(self, qtd=10):
        recipes = []
        for i in range(qtd):
            kwargs = {'slug': f'r{i}', 'author_data': {'username': f'u{i}'}}
            recipe = self.make_recipe(**kwargs)
            recipes.append(recipe)
        return recipes

class RecipeTestBase(TestCase, RecipeMixing):
    def setUp(self) -> None:
        return super().setUp()
