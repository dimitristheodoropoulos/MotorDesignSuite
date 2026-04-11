#!/bin/bash
set -e

echo "=== Phase 3 Docker Workflow ==="

# 1️⃣ Build/rebuild το image (με cache)
docker-compose build --no-cache phase3

# 2️⃣ Stop & remove τυχόν παλιό container
docker rm -f magnetic_phase3 >/dev/null 2>&1 || true

# 3️⃣ Run το container
docker-compose up --abort-on-container-exit

# 4️⃣ Copy έξω τα αποτελέσματα (αν χρειάζεται)
echo "=== Phase 3 Completed ==="
