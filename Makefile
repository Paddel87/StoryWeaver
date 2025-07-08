# StoryWeaver Makefile
# Vereinfacht Docker-Befehle und häufige Aufgaben

.PHONY: help build up down restart logs shell test clean dev prod

# Standardziel
.DEFAULT_GOAL := help

# Hilfe anzeigen
help: ## Zeigt diese Hilfe an
	@echo "StoryWeaver Docker Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Beispiel: make dev"

# Entwicklung
dev: ## Startet im Entwicklungsmodus
	docker-compose up -d
	@echo "✅ StoryWeaver läuft auf http://localhost:8501"

build: ## Baut das Docker Image neu
	docker-compose build

up: dev ## Alias für dev

down: ## Stoppt alle Container
	docker-compose down

restart: ## Neustart der Container
	docker-compose restart

logs: ## Zeigt Live-Logs
	docker-compose logs -f

shell: ## Öffnet Bash im Container
	docker-compose exec storyweaver bash

# Produktion
prod: ## Startet im Produktionsmodus
	docker build -t storyweaver:latest .
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stoppt Produktions-Container
	docker-compose -f docker-compose.prod.yml down

# Tests
test: ## Führt Tests im Container aus
	docker-compose exec storyweaver python -m pytest tests/

test-coverage: ## Tests mit Coverage-Report
	docker-compose exec storyweaver python -m pytest --cov=src --cov-report=html tests/

# Wartung
clean: ## Entfernt Container und Volumes
	docker-compose down -v
	docker system prune -f

clean-all: ## Entfernt ALLES (inkl. Images)
	docker-compose down -v --rmi all
	docker system prune -af

update: ## Aktualisiert Code und Container
	git pull
	docker-compose down
	docker-compose build --pull
	docker-compose up -d

# Daten
backup: ## Sichert Volumes
	@mkdir -p backups
	docker run --rm -v storyweaver_uploads:/data -v $(PWD)/backups:/backup alpine tar czf /backup/uploads_$(shell date +%Y%m%d_%H%M%S).tar.gz -C /data .
	docker run --rm -v storyweaver_spacy_cache:/data -v $(PWD)/backups:/backup alpine tar czf /backup/spacy_$(shell date +%Y%m%d_%H%M%S).tar.gz -C /data .
	@echo "✅ Backup erstellt in backups/"

# Entwicklung
lint: ## Prüft Code-Stil
	docker-compose exec storyweaver python -m flake8 src/

format: ## Formatiert Code mit Black
	docker-compose exec storyweaver python -m black src/ tests/

# Spezielle Befehle
cli: ## Führt CLI im Container aus
	docker-compose exec storyweaver python main.py examples/ -v

ui: ## Öffnet Browser mit UI
	@python -m webbrowser http://localhost:8501 || echo "Bitte öffne http://localhost:8501 im Browser"

health: ## Prüft Container-Gesundheit
	@docker-compose exec storyweaver curl -s localhost:8501/_stcore/health | jq . || echo "❌ Health Check fehlgeschlagen"

stats: ## Zeigt Container-Statistiken
	docker stats --no-stream $$(docker-compose ps -q)

# Docker Compose Overrides
dev-rebuild: ## Entwicklung mit Rebuild
	docker-compose up -d --build

dev-fresh: ## Entwicklung von Grund auf neu
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d 