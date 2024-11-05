include .env
export

lint: 
	poetry run black --check arista

format: 
	poetry run isort arista
	poetry run black arista

db.ip: 
	docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' aristadb

db.pwd:
	railway variables --kv | grep POSTGRES_PASSWORD

