# Setup for development environment

## Initial Setup

> This step only needs to be completed once

Install all dependecies and setup the db via `pipenv`. To do this run the following commands.

```bash
pipenv install --dev
pipenv run upgrade-db
```

## Run Backend

To run the backend execute the following command

```
pipenv run start
```

## Run Frontend

To run the frontend execute the following command

```
pipenv run start-js
```

## Deploy production build

To build the frontend and backend for use in production use the following command

```
pipenv run build
```

> TODO describe where the build-files are created and what further steps have to be taken