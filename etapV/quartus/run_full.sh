#!/bin/bash
set -e

# Python 3.13 repo
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Python 3.13
sudo apt install python3.13 python3.13-venv python3.13-dev -y

# Venv
python3.13 -m venv venv
source venv/bin/activate

# Icarus, cocotb
sudo apt-get install -y make iverilog
pip install cocotb

# Generowanie danych testowych
python gen_allowed_hosts.py
python generate_traffic.py
python gen_mem.py


# Czyszczenie potencjalnych pozostałości
make clean
# Symulacja
make