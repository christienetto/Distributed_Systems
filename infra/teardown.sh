#!/usr/bin/env bash
# Stop and remove the provisioned Multipass VMs, then purge.

set -euo pipefail

VMS=("database" "backend1" "backend2" "loadbalancer")

echo "Stopping VMs: ${VMS[*]}"
multipass stop "${VMS[@]}" || true

echo "Deleting VMs: ${VMS[*]}"
multipass delete "${VMS[@]}" || true

echo "Purging freed disk space..."
multipass purge

echo "Done."
