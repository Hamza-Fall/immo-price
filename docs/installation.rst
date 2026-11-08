Installation
============

Prérequis
---------

* Python 3.11 ou supérieur (testé jusqu'à 3.13)
* Git
* Poetry 2.x

Étapes
------

.. code-block:: bash

   git clone https://github.com/Hamza-Fall/immo-price.git
   cd immo-price
   poetry config virtualenvs.in-project true
   poetry install
   cp .env.example .env

Sous Windows PowerShell, remplacez ``cp`` par ``Copy-Item``.

Configuration
-------------

Éditez ``.env`` et remplacez ``change-me`` par une clé secrète, générée par
exemple avec :

.. code-block:: bash

   python -c "import secrets; print(secrets.token_urlsafe(32))"

Variables disponibles (préfixe ``IMMO_``) :

``IMMO_API_KEY``
   Clé exigée dans l'en-tête ``X-API-Key`` pour appeler ``/predict``.
``IMMO_MODEL_PATH``
   Chemin du modèle sauvegardé (par défaut ``models/model.joblib``).
``IMMO_DATA_DIR``
   Dossier des données téléchargées (par défaut ``data``).
``IMMO_LOG_LEVEL``
   Niveau de journalisation (par défaut ``INFO``).

Le fichier ``.env`` ne doit jamais être publié dans le dépôt.
