#!/bin/bash
set -e

# Zależności
sudo apt-get update
sudo apt-get install -y make iverilog python3-pip
pip install cocotb

# Generowanie danych
python3 gen_allowed_hosts.py
python3 generate_traffic.py
python3 gen_mem.py

# Symulacja
make