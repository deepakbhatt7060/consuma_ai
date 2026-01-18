## PreRequisites

- python3 version >= 3.10
- docker

## Setting up Backend

- cd BACKEND (Move to the directory)

## Run below commands to get MySQL DB container and verify whether mysql:8.0 container is in running state

- docker compose up -d
- docker ps

##Create a virtual env and Activate the env

- python3 -m venv venv
- source venv/bin/activate

## Verify the python, it should point to Backend/venv/bin/python

- which python

## Upgrade pip and install packages

- pip install --upgrade pip
- pip install .

## Upgrade db schema

- alembic upgrade head

## Set the below env variable to run cron for scheduling failed_callbacks only on one worker

export RUN_SCHEDULER=true

## Run the server

- uvicorn app.main:app --workers 4

## Use below website that provides callback url for sync test feature

Note- https://webhook.site/
