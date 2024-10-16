DEVICE_FAMILY = "Stratix IV"
DEVICE_NAME = "EP4SGX530NF45C4ES"

TURN_OFF_DSPS = """set_global_assignment -name DSP_BLOCK_BALANCING_IMPLEMENTATION "LOGIC ELEMENTS"
set_global_assignment -name MAX_BALANCING_DSP_BLOCKS 0
set_global_assignment -name AUTO_DSP_RECOGNITION OFF
"""

EXECUTE_FLOW_TYPE = "implement" # change accordingly before use