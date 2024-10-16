"""
Defaults that are shared across multiple implementations.
"""

DEFAULTS_EXP = {
    'stdout_file': 'std.out',
    'stderr_file': 'std.err',
}

DEFAULTS_EXP_VTR = {
    **DEFAULTS_EXP,
    'seed': 1127,
    'clean': True,
    'dry_run': False,
    'ending': None,
    'allow_skipping': False,
    'avoid_mult': True,
    'force_denser_packing': False,
    'adder_cin_global': True,
    'soft_multiplier_adders': False,
    'compressor_tree_type': 'wallace',
}

DEFAULTS_EXP_QUARTUS = {
    **DEFAULTS_EXP,
    'output_dir': 'outputs',
    'execute_flow_type': 'implement',
}

DEFAULTS_TCL = {
    'output_dir': 'output',
    'parallel_processors_num': 4,
    'execute_flow_type': 'implement',
}

# Wrapper defaults
DEFAULTS_WRAPPER = {
    'constant_weight': True,
    'sparsity': 0.0,
    'clock': 1,
    'tree_base': 2,
}
DEFAULTS_WRAPPER_CONV = {
    'buffer_stages': 0,
    'kernel_only': False,
    'separate_filters': False,
    **DEFAULTS_WRAPPER
}