# FastAPI Template

Template de base pour un backend FastAPI : auth JWT, PostgreSQL (SQLAlchemy async), Redis, migrations Alembic, tests, CI.

## Démarrage rapide

```bash
cp .env.example .env          # ajuster SECRET_KEY en prod
make docker-up                 # postgres + redis (docker-compose.yml)
uv sync --all-groups
make migrate                   # applique les migrations
make dev                       # lance le serveur avec reload
```

Équivalent npm si `make` n'est pas dispo (Windows natif) : `npm run docker:up`, `npm run migrate`, `npm run dev`.

Docs interactives : http://localhost:8000/docs (visible seulement si `DEBUG=true`).

## Structure

```
app/
  main.py              point d'entrée unique — instancie FastAPI, branche middlewares/exceptions/routers
  core/
    config.py          Settings (pydantic-settings), chargé depuis .env
    db.py               engine + session SQLAlchemy async
    redis.py            client Redis async
    security.py          hash de mot de passe (bcrypt) + JWT encode/decode
    auth.py              dépendance get_current_user_id (vérifie le JWT, ou bypass si BYPASS_AUTH=true)
    exceptions.py         AppException et sous-classes + handlers globaux
    logging.py            setup_logging() / get_logger()
    constant.py            constantes globales (pagination, etc.)
  models/
    base.py               Base SQLAlchemy + AppModel (id UUID + created_at/updated_at)
  schemas/
    base.py                AppSchema — base Pydantic obligatoire pour tout schema du projet
    pagination.py           Page[T] générique pour les réponses paginées
  services/
    base.py                 BaseService[Model] — CRUD générique (get_by_id, get_all, create, delete)
  api/
    router.py                api_router central, agrège tous les sous-routers
    dependancies.py           DbSession, CurrentUserId, RedisClient — dépendances typées Annotated
    routes/                   un fichier par feature (health.py, info.py, ...)
    schemas/                  schemas de requête/réponse par route, héritent de AppSchema
  middlewares/
    cors.py                   CORS (origins libres en DEBUG, ALLOWED_ORIGINS sinon)
    request_id.py              header X-Request-ID sur chaque requête
    logging.py                  log méthode/path/status/durée par requête
alembic/                       migrations (async, configuré pour lire DATABASE_URL depuis Settings)
scripts/                       scripts standalone (seed, maintenance) — pattern dans seed_db.py
tests/                         conftest.py fournit un client HTTP avec DB/Redis mockés
```

## Conventions à respecter

- **Schemas** : toujours hériter de `AppSchema` ([app/schemas/base.py](app/schemas/base.py)), jamais `pydantic.BaseModel` directement.
- **Schemas de route** vivent dans `app/api/schemas/`, co-localisés avec leur route. Les schemas génériques réutilisables (ex: `Page`) vivent dans `app/schemas/`.
- **Logique métier** dans des services héritant de `BaseService[Model]`, pas dans les routes.
- **Exceptions métier** : lever une sous-classe d'`AppException` (`NotFoundException`, `ConflictException`, etc.) plutôt qu'`HTTPException` directement.
- **Dépendances de route** : utiliser les alias typés de `app/api/dependancies.py` (`DbSession`, `CurrentUserId`, `RedisClient`) plutôt que `Depends(...)` brut.

## Auth — mode bypass

`BYPASS_AUTH=true` (valeur par défaut en dev) désactive complètement la vérification JWT — chaque requête est traitée comme authentifiée avec un user id fixe. **Le démarrage de l'app échoue volontairement si `BYPASS_AUTH=true` et `DEBUG=false`** ([app/core/config.py](app/core/config.py)), pour empêcher un oubli en production.

## Commandes utiles

| Make | npm | Description |
|---|---|---|
| `make dev` | `npm run dev` | serveur avec reload |
| `make test` | `npm run test` | suite de tests |
| `make lint` | `npm run lint` | ruff check + format check |
| `make format` | `npm run format` | corrige automatiquement |
| `make migration name="..."` | `npm run migration -- "..."` | génère une migration Alembic |
| `make migrate` | `npm run migrate` | applique les migrations |
| `make docker-up` / `docker-down` | `npm run docker:up` / `docker:down` | postgres + redis locaux |

## CI

[.github/workflows/ci.yml](.github/workflows/ci.yml) : lint (ruff) puis tests (avec postgres/redis éphémères), sur chaque push/PR vers `main`.
