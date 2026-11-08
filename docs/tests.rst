Tests et couverture
===================

.. code-block:: bash

   poetry run pytest

La commande exécute les tests, affiche la couverture dans le terminal, écrit
``coverage.xml`` et le rapport HTML ``htmlcov/index.html``. Elle échoue si la
couverture est inférieure à 75 %.

Qualité du code
---------------

.. code-block:: bash

   poetry run ruff check .
   poetry run ruff format --check .
   poetry run mypy src
   poetry run pre-commit run --all-files

Génération de cette documentation
---------------------------------

.. code-block:: bash

   poetry run sphinx-build -b html docs docs/_build/html

La page d'accueil est ``docs/_build/html/index.html``.
