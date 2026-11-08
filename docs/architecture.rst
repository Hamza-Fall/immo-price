Architecture
============

Flux de données
---------------

.. code-block:: text

   data.gouv.fr --> data_loading --> preprocessing --> train --> model.joblib
                                                                     |
                                       client HTTP --> API FastAPI --+--> predict

Modules
-------

``config``
   Paramètres lus dans l'environnement ou dans ``.env`` (préfixe ``IMMO_``).
``logging_config``
   Format et niveau des logs.
``data_loading``
   Téléchargement et lecture des fichiers DVF d'un département.
``preprocessing``
   Nettoyage, calcul du prix au m² et séparation temporelle.
``train``
   Pipeline scikit-learn, évaluation face à une baseline, sauvegarde.
``predict``
   Chargement du modèle et prédiction.
``api``
   Application FastAPI, schémas Pydantic et authentification par clé API.

Choix de conception
-------------------

* Séparation temporelle : entraînement sur les années passées, test sur la
  dernière année.
* Le prétraitement est inclus dans le pipeline scikit-learn : le modèle
  sauvegardé accepte directement les données brutes de l'API.
* La clé API et les chemins viennent de l'environnement, jamais du code.
