# fajerwoll
## Środowisko testowe
Środowisko testowe znajduje się razem z resztą potrzebnych plików w folderze etapV. Aby je uruchomić, należy z poziomu linuxa:
* przejść do głównego katalogu: `cd etapV/quartus`,
* nadać uprawnienia do wykonywania skryptowi uruchamiającemu: `chmod +x run_full.sh`:,
* wykonać plik: `./run_full.sh`.
`run_full.sh` przed uruchomieniem symulacji instaluje wersję python3.13 wymaganą dla cocotb, cocotb oraz icarus.
W następnych wykonaniach można używać pliku `run_sim.sh`, który nie próbuje instalować zależności.
## Wymagane zależności (Linux)
* iverilog
* python3
* python3-pip

## Wymagane zależności (Python)
* cocotb

## Model firewall'a
W `model` znajdują się skrypty w języku Python modelujące działanie firewall'a i testujące go dla wygenerowanego ruchu.
