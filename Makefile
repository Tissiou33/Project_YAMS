.PHONY: up down logs test lint admin

up:        ## Démarre db + redis + API
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f backend

test:      ## Tests backend
	cd backend && pytest -q

admin:     ## Back-office React (dev)
	cd admin && npm install && npm run dev
