include .env
export

.PHONY: api

URL=https://open-api-v3.coinglass.com/api/futures/supported-coins

api:
	curl -H "CG-API-KEY: $(API_KEY)" $(URL)


lint: 
	poetry run ruff check arista

format: lint
	poetry run ruff format arista

