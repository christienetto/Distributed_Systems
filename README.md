# Distributed Text Exitor

## Virtual Environment

### Prerequisites

Install Multipass [here](https://canonical.com/multipass), or via Homebrew:

```bash
brew install --cask multipass
```

### Launch

To launch virtual machines, run:

```bash
./infra/provision.sh
```

Note that this may take a while. Access the app via the printed URL once everything is ready.

### Teardown

To stop and delete all VMs, run:

```bash
./infra/teardown.sh
```

## Local Development

Running the VMs for development is probably too slow. Instead, you can run everything with Docker:

```bash
docker compose up --build # Access the app in http://localhost:8000
```

Or, run frontend separately, with hot reload (see `code/frontend/README.md`).
