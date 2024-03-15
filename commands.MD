# Criar APP

    python3 manage.py startapp recipes

# Install Venv into your project

    python3 -m venv venv

# Activate Venv

    .  venv/bin/activate

# List Libs installed on your venv project, after activate venv

    pip3 freeze

# Install lib with pip

    pip3 install pytest

# Deactivate Venv

    deactivate

# Run Django server local

    python3 manage.py runserver

# Generate statics files

    python3 manage.py collectstatic

# Run tests with Coverage

    coverage run -m pytest

    coverage run manage.py test

    coverage html (Open report)

# Open python sheel (with venv activated) to Duplicate Recipes quickly

    python3 manage.py shell

    >>> from recipes.models import Recipe
    >>> r= Recipe.objects.get(id=3)
    >>> r.id = None
    >>> r.save()

# Command to Generate Secret 

    python3 -c "import string as s;from random import SystemRandom as sr;print(''.join(sr().choices(s.ascii_letters + s.punctuation, k=64)))"

# Install Pip dependencies from file 

    pip3 install -r requirements.txt

# Export dependencis used into a file 

    pip3 freeze > requirements.txt 

# Run Pytest with mark 

    After configurated on pyest.ini the mark. : 

    functional_test: Run tests that are selenium based

    Command: (Execute only this mark)

    pytest -m 'functional_test'

    Command: (Execute expect the mark)

    pytest -m 'not functional_test'

# Run Pytest , only one test by its name 

    pytest -k 'test_recipe_home_page_without_recipes_not_found_message'
