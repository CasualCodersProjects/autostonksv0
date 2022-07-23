default:
    just --list

build:
    docker-compose build

run:
    docker-compose up -d

stop:
    docker-compose down

logs container="":
    if [ -z "{{container}}" ]; then docker-compose logs -f; else docker logs {{container}} -f; fi

build-frontend:
    docker build frontend -t autostonks-frontend:latest

run-frontend:
    docker run --rm -d -p 3000:3000 autostonks-frontend:latest

stop-frontend:
    docker stop autostonks-frontend

build-api:
    docker build backend -f backend/Dockerfile.api -t autostonks-api:latest

run-api:
    docker run --rm -d -p 8080:8080 --name autostonks-api autostonks-api:latest

stop-api:
    docker stop autostonks-api

build-bot:
    docker build backend -f backend/Dockerfile.bot -t autostonks-bot:latest

run-bot:
    docker run --rm -d --name autostonks-bot --env-file=.env autostonks-bot:latest

stop-bot:
    docker stop autostonks-bot

run-database:
    docker run --rm --name autostonks-database -p 5432:5432 -e POSTGRES_DB=autostonks -e POSTGRES_PASSWORD=password -d postgres

stop-database:
    docker stop autostonks-database

install-dev:
    npm i -g yarn
    pip3 install -U pipenv pip

install-frontend:
    cd frontend
    yarn
    cd ..

install-backend:
    cd backend
    pipenv install
    cd ..

install: install-dev install-frontend install-backend