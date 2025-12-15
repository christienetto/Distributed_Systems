#!/usr/bin/env bash
# Bring up MongoDB, two backend VMs, and an Nginx load balancer using Multipass + Docker.

set -euo pipefail

DATABASE_VM="database"
BACKEND_VM1="backend1"
BACKEND_VM2="backend2"
LOADBALANCER_VM="loadbalancer"
COMPOSE_PATH="$(realpath "docker-compose.yml")"
CODE_DIR="$(realpath "code")"
REMOTE_COMPOSE="/home/ubuntu/docker-compose.yml"
IMAGE="${IMAGE:-24.04}"
DISK="${DISK:-10G}"

ensure_vm() {
  local name="$1"
  if multipass info "$name" >/dev/null 2>&1; then
    echo "VM $name already exists."
  else
    echo "Launching VM $name..."
    multipass launch "$IMAGE" --name "$name" --disk "$DISK"
  fi
}

install_docker() {
  local name="$1"
  echo "Installing Docker inside $name..."
  multipass exec "$name" -- bash -lc "
    set -e
    sudo apt-get update -y
    sudo apt-get install -y curl
    if ! command -v docker >/dev/null 2>&1; then
      curl -fsSL https://get.docker.com | sudo sh
    fi
    if ! docker compose version >/dev/null 2>&1; then
      sudo apt-get install -y docker-compose || sudo pip3 install docker-compose
    fi
  "
}

copy_compose() {
  local name="$1"
  local remote_dir
  remote_dir="$(dirname "$REMOTE_COMPOSE")"
  multipass exec "$name" -- bash -lc "mkdir -p '$remote_dir'"
  multipass transfer "$COMPOSE_PATH" "$name:$REMOTE_COMPOSE"
}

copy_code() {
  local name="$1"
  if [[ -d "$CODE_DIR" ]]; then
    multipass transfer --recursive "$CODE_DIR" "$name:code"
  fi
}

start_database() {
  local name="$1"
  echo "Starting MongoDB on $name..."
  multipass exec "$name" -- bash -lc "
    cd /home/ubuntu
    MONGO_REPLICA_HOST=\$(hostname -I | awk '{print \$1\":27017\"}')
    sudo env MONGO_REPLICA_HOST=\"\$MONGO_REPLICA_HOST\" docker compose -f \"$REMOTE_COMPOSE\" up -d mongodb mongo-init-replica
  "
}

start_backend() {
  local name="$1"
  local database_ip="$2"
  echo "Starting backend on $name (DB at $database_ip)..."
  multipass exec "$name" -- bash -lc "
    cd /home/ubuntu
    sudo env \
      MONGODB_URI=mongodb://$database_ip:27017/?replicaSet=rs0 \
      VITE_API_BASE_URL=\${VITE_API_BASE_URL:-} \
      VITE_WS_BASE=\${VITE_WS_BASE:-} \
      docker compose -f \"$REMOTE_COMPOSE\" up -d --force-recreate server
  "
}

# The app can be scaled horizontally by adding more backend servers in the upstream backend block.
start_loadbalancer() {
  local name="$1"
  local backend1_ip="$2"
  local backend2_ip="$3"
  echo "Starting load balancer on $name (backends: $backend1_ip, $backend2_ip)..."
  multipass exec "$name" -- bash -lc "
    cat > /home/ubuntu/nginx.conf <<'EOF'
upstream backend {
    server BACKEND1_IP:8000;
    server BACKEND2_IP:8000;
}
server {
    listen 80;
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }
}
EOF
    sed -i 's/BACKEND1_IP/$backend1_ip/' /home/ubuntu/nginx.conf
    sed -i 's/BACKEND2_IP/$backend2_ip/' /home/ubuntu/nginx.conf
    sudo docker rm -f lb >/dev/null 2>&1 || true
    sudo docker run -d --name lb -p 8080:80 -v /home/ubuntu/nginx.conf:/etc/nginx/conf.d/default.conf:ro nginx:1.25
  "
}

echo "=== Provisioning Database VM ($DATABASE_VM) ==="
ensure_vm "$DATABASE_VM"
install_docker "$DATABASE_VM"
copy_compose "$DATABASE_VM"
start_database "$DATABASE_VM"

echo "=== Provisioning Backend VM ($BACKEND_VM1) ==="
ensure_vm "$BACKEND_VM1"
install_docker "$BACKEND_VM1"
copy_compose "$BACKEND_VM1"
copy_code "$BACKEND_VM1"

echo "=== Provisioning Backend VM ($BACKEND_VM2) ==="
ensure_vm "$BACKEND_VM2"
install_docker "$BACKEND_VM2"
copy_compose "$BACKEND_VM2"
copy_code "$BACKEND_VM2"

DATABASE_IP="$(multipass info "$DATABASE_VM" | awk '/IPv4/{print $2; exit}')"

start_backend "$BACKEND_VM1" "$DATABASE_IP"
start_backend "$BACKEND_VM2" "$DATABASE_IP"

BACKEND1_IP="$(multipass info "$BACKEND_VM1" | awk '/IPv4/{print $2; exit}')"
BACKEND2_IP="$(multipass info "$BACKEND_VM2" | awk '/IPv4/{print $2; exit}')"

echo "=== Provisioning LB VM ($LOADBALANCER_VM) ==="
ensure_vm "$LOADBALANCER_VM"
install_docker "$LOADBALANCER_VM"
start_loadbalancer "$LOADBALANCER_VM" "$BACKEND1_IP" "$BACKEND2_IP"

echo "All VMs ready."
LB_IP="$(multipass info "$LOADBALANCER_VM" | awk '/IPv4/{print $2; exit}')"
echo "Access the app at: http://$LB_IP:8080/"
