VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
DATE ?= 2026-11-27
DELAY ?= 4

.PHONY: help setup test dev run scheduler docker-up docker-down docker-logs clean

help: ## Tampilkan daftar perintah yang tersedia
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Buat .venv, install dependencies, dan siapkan .env
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	@if [ ! -f .env ]; then cp .env.example .env && echo "File .env dibuat dari .env.example. Silakan isi email & password."; fi

test: ## Jalankan unit test
	$(PYTHON) -m unittest discover -s tests -v

dev: ## Uji coba mode development (browser tampil, pelan, tanpa submit). Contoh: make dev DATE=2026-11-27 DELAY=4
	$(PYTHON) main.py --run-now --date $(DATE) --dry-run --headed --step-delay $(DELAY)

run: ## Jalankan presensi hari ini sesuai konfigurasi .env
	$(PYTHON) main.py --run-now

scheduler: ## Jalankan service scheduler (Senin-Jumat 15:00 WIB)
	$(PYTHON) scheduler.py

docker-up: ## Jalankan di Docker (homelab background)
	docker compose up -d --build

docker-down: ## Hentikan container Docker
	docker compose down

docker-logs: ## Lihat log container Docker
	docker compose logs -f

clean: ## Hapus cache dan folder logs
	rm -rf __pycache__ src/__pycache__ tests/__pycache__ logs
