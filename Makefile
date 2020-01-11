.PHONY: all clean cpu

OUTDIR = ./iverilog
TBDIR = ./src/tb
SRCDIR = ./src
FLAGS = -Wall

TESTBENCHES =  $(wildcard $(TBDIR)/*.v)

TESTBENCH_OBJECTS =  $(addprefix $(OUTDIR)/,$(notdir $(TESTBENCHES:.v=.vvp)))

MODULES =  $(wildcard $(SRCDIR)/*.v)
#MODULES += $(wildcard ./more_modules/*.v) # <--- add more from other directories like this

# compile and run every testbench in the tb directory
all: $(TESTBENCH_OBJECTS)
	for tb in $^ ; do \
		./$$tb;\
	done

# assumes the test bench module's name matches the file name before the file extension
$(OUTDIR)/%.vvp: $(TBDIR)/%.v $(MODULES) | $(OUTDIR)
	iverilog -o $@ -s $* $^ $(FLAGS)

$(OUTDIR):
	mkdir -p $(OUTDIR)

clean:
	-rm -rf $(OUTDIR) *.vcd *.log *.trace
