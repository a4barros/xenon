# Xenon

E2E encrypted password manager.

<img src="./doc/diagram.svg">

## Install (development)

1. Deploy the database container

```bash
docker compose build db
docker compose up db -d
```

2. Activate the venv and install dependencies

```bash
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

3. Run in dev mode with debugger

Click on the "Run and debug" button on VSCode to run the server using the config
provided on `.vscode/launch.json`