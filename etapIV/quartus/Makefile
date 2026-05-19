# Makefile
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Dodajemy wszystkie pliki Veriloga
VERILOG_SOURCES += $(PWD)/hw_hash.v
VERILOG_SOURCES += $(PWD)/layer1_bloom.v
VERILOG_SOURCES += $(PWD)/layer2_cuckoo.v
VERILOG_SOURCES += $(PWD)/fajerwoll.v

# Moduł nadrzędny w Verilogu
TOPLEVEL = fajerwoll

# Nazwa pliku Pythona z testbenchem (bez rozszerzenia .py)
MODULE = test_aegis_zero

# Import reguł Cocotb
include $(shell cocotb-config --makefiles)/Makefile.sim