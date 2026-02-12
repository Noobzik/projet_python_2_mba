# Instructions Docker

## Construire l'image

```powershell
docker build -t banking-api:1.0.0 .
```

## Exécuter le conteneur

```powershell
# Exécution simple
docker run -p 8000:8000 banking-api:1.0.0

# Avec volume pour les données
docker run -p 8000:8000 -v ${PWD}/data:/app/data:ro banking-api:1.0.0
```

## Utiliser Docker Compose

```powershell
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Voir les logs
docker-compose logs -f

# Rebuild
docker-compose up --build
```

## Vérifier le statut

```powershell
# Vérifier que le conteneur est en cours d'exécution
docker ps

# Vérifier la santé
docker inspect banking-api --format='{{.State.Health.Status}}'

# Tester l'API
curl http://localhost:8000/api/system/health
```
