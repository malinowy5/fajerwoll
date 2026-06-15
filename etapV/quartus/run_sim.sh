#!/bin/bash
set -e

# Aktywacja wirtualnego środowiska
source venv/bin/activate

# Generowanie danych
python gen_allowed_hosts.py
python generate_traffic.py
python gen_mem.py

# Symulacja
make clean
make