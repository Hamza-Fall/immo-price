Utilisation
===========

Commandes
---------

.. code-block:: bash

   poetry run immo-download --departement 94 --years 2023 2024 2025
   poetry run immo-train --departement 94 --years 2023 2024 2025
   poetry run immo-api

L'API écoute sur ``http://127.0.0.1:8000``. La documentation Swagger est
disponible sur ``/docs``.

Endpoints
---------

``GET /health``
   Renvoie l'état du service et indique si le modèle est chargé.

``POST /predict``
   Estime le prix d'un appartement. L'en-tête ``X-API-Key`` est obligatoire.

Exemple d'appel :

.. code-block:: bash

   curl -X POST http://127.0.0.1:8000/predict \
     -H "X-API-Key: VOTRE_CLE" -H "Content-Type: application/json" \
     -d '{"surface": 45, "nombre_pieces": 2, "code_postal": "94270", "annee": 2025}'

Codes de réponse
----------------

* ``200`` : succès
* ``401`` : clé API absente ou invalide
* ``422`` : entrée invalide
* ``503`` : modèle non chargé ou clé API non configurée
