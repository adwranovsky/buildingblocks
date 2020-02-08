# Building Blocks
## Purpose
This project serves as a way to refresh myself on FPGA design, and to evaluate MyHDL.
## Examples
```python
from buildingblocks import tb, rtl

# Run some testbenches
tb.uart.tx.run()
tb.uart.rx.run()

# Convert to Verilog for synthesis
rtl.uart.convert.tx()
rtl.uart.convert.rx()
```
