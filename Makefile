include .env
export

.PHONY: api

URL=https://open-api-v3.coinglass.com/api/futures/supported-coins

api:
	curl -H "CG-API-KEY: $(API_KEY)" $(URL)

