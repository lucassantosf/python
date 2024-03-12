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