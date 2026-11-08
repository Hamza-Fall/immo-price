# Immo Price : estimation du prix d'un appartement

![CI](https://github.com/Hamza-Fall/immo-price/actions/workflows/ci.yml/badge.svg)

Application Python Data/ML complète : préparation des données DVF,
entraînement d'un modèle scikit-learn et exposition des prédictions par une
API REST FastAPI. Projet du module Software Engineering for Data (SOENFO),
réalisé en binôme : <Amsata Fall> et <Yi xu>.

## Cas d'usage

Estimer le prix d'un appartement du Val-de-Marne (94) à partir de sa surface,
de son nombre de pièces, de son code postal et de l'année de la vente.

## Dataset

- **Source** : Demandes de valeurs foncières géolocalisées (DVF), publiées par
  Etalab à partir des données de la DGFiP sur data.gouv.fr :
  https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/
- **Licence** : Licence Ouverte 2.0 (Etalab), réutilisation libre avec mention
  de la source.
- **Contexte** : transactions immobilières, mises à jour deux fois par an.
- **Périmètre** : département 94 (Val-de-Marne), années 2023 à 2025.
- **Volumétrie** : 139 865 lignes brutes, 28 266 ventes d'appartements retenues
  après nettoyage (9 800 en 2023, 8 409 en 2024, 10 057 en 2025).
- **Tâche** : régression du prix au m².
- **Données personnelles** : aucune donnée sensible, les noms des parties ne
  figurent pas dans les fichiers.
- **Récupération** : par script (`immo-download`), les données ne sont pas dans
  Git.

### Justification et limites

- Source officielle, ouverte et volumineuse, qui permet une séparation
  temporelle : entraînement sur 2023 et 2024, test sur 2025.
- Une vente peut regrouper plusieurs biens avec un prix global : ces ventes
  sont exclues, ainsi que les maisons, les échanges et les lignes incomplètes.
- Les valeurs aberrantes sont filtrées par seuils (surface de 9 à 300 m²,
  prix de 1 000 à 30 000 €/m²).
- Peu de caractéristiques du bien (pas d'étage, d'état ni de DPE) : la
  précision du modèle est limitée.
- Le prix dépend fortement de la localisation fine et de la période, alors que
  le modèle ne connaît que le code postal et l'année.

## Installation

Prérequis : Python 3.11 ou supérieur, Git, Poetry 2.x.

```bash
git clone https://github.com/Hamza-Fall/immo-price.git
cd immo-price
poetry config virtualenvs.in-project true
poetry install
cp .env.example .env        # PowerShell : Copy-Item .env.example .env
```

Éditez `.env` et remplacez `change-me` par une clé secrète, par exemple avec
`python -c "import secrets; print(secrets.token_urlsafe(32))"`.
**Ne commitez jamais `.env`.**

## Commandes

```bash
poetry run immo-download --departement 94 --years 2023 2024 2025   # données
poetry run immo-train --departement 94 --years 2023 2024 2025      # modèle
poetry run immo-api                                                # API
```

Les données sont téléchargées dans `data/` et le modèle est sauvegardé dans
`models/` (`model.joblib` et `metrics.json`). Ces dossiers sont ignorés par Git.

## Résultats du modèle

Modèle : `GradientBoostingRegressor` dans un pipeline scikit-learn (encodage
one-hot du code postal). Évaluation sur 2025, année non vue à l'entraînement.

| Métrique | Modèle | Baseline (prix médian) |
|---|---|---|
| MAE (€/m²) | 872 | 1 542 |
| RMSE (€/m²) | 1 269 | - |
| R² | 0,62 | - |

18 209 ventes pour l'entraînement, 10 057 pour le test.

## Utilisation de l'API

Documentation Swagger : http://127.0.0.1:8000/docs

```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/predict \
  -H "X-API-Key: VOTRE_CLE" -H "Content-Type: application/json" \
  -d '{"surface": 45, "nombre_pieces": 2, "code_postal": "94270", "annee": 2025}'
```

Exemple de réponse :

```json
{"prix_m2": 5614.26, "prix_estime": 252641.87}
```

PowerShell :

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/predict -Method Post `
  -Headers @{"X-API-Key"="VOTRE_CLE"} -ContentType "application/json" `
  -Body '{"surface":45,"nombre_pieces":2,"code_postal":"94270","annee":2025}'
```

Codes de réponse : 200 succès, 401 clé invalide, 422 entrée invalide,
503 modèle non chargé ou clé non configurée.

## Qualité, tests et couverture

```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy src
poetry run pytest          # échoue sous 75 % de couverture
```

Les rapports sont écrits dans le terminal, `coverage.xml` et
`htmlcov/index.html`. Couverture actuelle : <100> %.
Hooks de commit : `poetry run pre-commit install`.

## Documentation technique

```bash
poetry run sphinx-build -b html docs docs/_build/html
```

Ouvrir `docs/_build/html/index.html`.

## Packaging

```bash
poetry build               # produit dist/*.whl et dist/*.tar.gz
```

## Intégration continue

Le workflow GitHub Actions (`.github/workflows/ci.yml`) s'exécute à chaque
push et pull request : Ruff, mypy, pytest avec couverture, Sphinx et
`poetry build`.

## Structure du dépôt

```
src/immo_price/    code (config, data_loading, preprocessing, train, predict, api/)
tests/             tests pytest
docs/              documentation Sphinx
.github/workflows/ intégration continue
```

## Déclaration d'utilisation de l'IA générative

Nous avons utilisé l'assistant Claude (Anthropic) pour : choisir le jeu de
données, proposer l'architecture du projet, générer une première version du
code, des tests et des fichiers de configuration, et nous guider dans
l'installation des outils.
Nous avons exécuté l'ensemble du code et des tests, vérifié les résultats
(tests, couverture, appels à l'API, CI)
