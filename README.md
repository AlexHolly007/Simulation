# Simulation Game

Live deployment on AWS: https://sim-alex.com

Interactive, open-ended “choose your own adventure” played through short prompts. The FastAPI backend calls OpenAI for concise story beats and image generation, while a small microservice injects weighted randomness to keep the narrative surprising. A static frontend (HTML/CSS/JS) displays the text and images.

## Features
- GPT-driven text turns with lightweight state tracking and tone guidance
- GPT Image generation that follows recent actions and style cues
- Random event picker microservice to vary plot turns
- Frontend served via Nginx; FastAPI services exposed behind the gateway

## Quickstart (local Python)
1) Python 3.11+
2) Install deps:
	```
	pip install -r requirements.txt
	```
3) Create .env in repo root:
	```
	OPENAI_API_KEY=<your key>
	```
4) Run the microservice, then the main API (default localhost ports 12121 and 45454):
	```
	python backend/Microservice.py
	python backend/app.py
	```
5) Open frontend/index.html directly or serve it; API base defaults to http://localhost:45454.

## Docker / Compose
- Build and run all services (main API, microservice, Nginx):
  ```
  docker compose up --build
  ```
- Ports: Nginx on 80/443; main API exposed internally on 45454; microservice on 12121.
- Nginx serves frontend static assets from ./frontend and proxies to the FastAPI services. Certbot volumes are wired for TLS renewal (certs/ and certbot-data/).

## Environment
- OPENAI_API_KEY (required)
- MICROSERVICE_URL optional (defaults to http://localhost:12121 or docker service name)

## Repo Map
- backend/app.py: FastAPI text/image engine endpoints
- backend/Microservice.py: weighted random selector API
- frontend/: static UI (index.html, css, script.js)
- docker-compose.yml: sim-main-api, sim-micro-api, nginx, certbot
- Dockerfile.app / Dockerfile.micro: FastAPI containers
