# Makefile

# defaults
SIM ?= icarus
# SIM ?= verilator
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/delta_cycles.v

TOPLEVEL = flipflop

# MODULE is the basename of the Python test file(s)
MODULE = delta_cycles

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim