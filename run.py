import structure.consts.keys as keys

from runs.vtr_denoised_v1 import run_vtr_denoised_v1

import runs.benchmarks.kratos as kratos
import runs.benchmarks.kratos_mini as mini

# v1.2
from impl.arch.stratix_IV.gen_exp_fpop import GenExpFpopArchFactory

from impl.design.conv_1d.fu import Conv1dFuDesign
from impl.design.conv_1d.pw import Conv1dPwDesign
from impl.design.conv_2d.fu import Conv2dFuDesign
from impl.design.conv_2d.rp import Conv2dRpDesign
from impl.design.conv_2d.pw import Conv2dPwDesign
from impl.design.gemmt.fu import GemmTFuDesign
from impl.design.gemmt.rp import GemmTRpDesign
from impl.design.gemms import GemmSDesign

import os.path as path

BASE_PARAMS = {
    keys.KEY_EXP: {
        'verilog_search_dir': path.join(path.dirname(path.realpath(__file__)), 'verilog'),
        'allow_skipping': True,
        'adder_cin_global': True,
        # ... additional Experiment.run() parameters
    },
    keys.KEY_ARCH: {
        # fixed architecture parameters for both baseline and explored
        'lut_size': 5,
        'cin_mux_stride': 1,
    },
    keys.KEY_DESIGN: {
        'sparsity': [0, 0.5, 0.9],
        # 'sparsity': 0.5,
        'data_width': 4
    }
}

VARIABLE_ARCH_PARAMS = dict(
    ble_count=list(range(2, 21)),
    # CLB_groups_per_xb=list(range(1, 5)),
)

DESIGN_LIST = [
    # Mini benchmarks
    # (Conv1dFuDesign(), mini.get_conv_1d_fu_params(BASE_PARAMS)),
    # (Conv1dPwDesign(), mini.get_conv_1d_pw_params(BASE_PARAMS)),
    # (Conv2dFuDesign(), mini.get_conv_2d_fu_params(BASE_PARAMS)),
    # (Conv2dRpDesign(), mini.get_conv_2d_rp_params(BASE_PARAMS)),
    # (Conv2dPwDesign(), mini.get_conv_2d_pw_params(BASE_PARAMS)),
    # (GemmTFuDesign(), mini.get_gemmt_fu_params(BASE_PARAMS)),
    # (GemmTRpDesign(), mini.get_gemmt_rp_params(BASE_PARAMS)),
    # (GemmSDesign(), mini.get_gemms_params(BASE_PARAMS)),

    # Kratos benchmarks
    (Conv1dFuDesign(), kratos.get_conv_1d_fu_params(BASE_PARAMS)),
    # (Conv1dPwDesign(), kratos.get_conv_1d_pw_params(BASE_PARAMS)),
    # (Conv2dFuDesign(), kratos.get_conv_2d_fu_params(BASE_PARAMS)),
    # (Conv2dRpDesign(), kratos.get_conv_2d_rp_params(BASE_PARAMS)),
    # (Conv2dPwDesign(), kratos.get_conv_2d_pw_params(BASE_PARAMS)),
    (GemmTFuDesign(), kratos.get_gemmt_fu_params(BASE_PARAMS)),
    # (GemmTRpDesign(), kratos.get_gemmt_rp_params(BASE_PARAMS)),
    (GemmSDesign(), kratos.get_gemms_params(BASE_PARAMS)),
]

run_vtr_denoised_v1(
    design_list=DESIGN_LIST,
    variable_arch_params=VARIABLE_ARCH_PARAMS,
    # group_normalize_on=['sparsity'],
    # normalize_each_group_on=dict(ble_count=10),
    filter_params_baseline=['sparsity'],
    group_cols_short_labels=dict(sparsity='s'),
    filter_results=['fmax', 'cpd', 'rcw', 'area_total', 'area_total_used', 'lero', 'lelr_frac', 'lelo_frac', 'lero_frac', 'nets_absorbed_frac'],
    filter_blocks=['clb', 'fle', 'flutS.ff', 'arithmetic.ff', 'ff'],
    num_parallel_tasks=16,
    avoid_norm=['clb_avg_util', 'lero', 'lelr_frac', 'lelo_frac', 'lero_frac', 'nets_absorbed_frac', 'flutS.ff', 'arithmetic.ff', 'ff'],
    translations={
        'ble_count': 'N',
        'fmax': 'Fmax',
        'cpd': 'CPD',
        'rcw': 'Route Channel Width',
        'clb': 'CLB Count',
        'fle': 'FLE Count',
        'area_total': 'Total area (logic tiles + routing)',
        'area_total_used': 'Total area (used logic area + routing)',
        'lero': 'LEs as Register only',
        'lelr_frac': '% of LEs as Logic and Register',
        'lelo_frac': '% of LEs as Logic only',
        'lero_frac': '% of LEs as Register only',
        'nets_absorbed_frac': '% of Logical Nets absorbed',
        'adp': 'Area-Delay Product (logic tiles + routing)',
        'adp_used': 'Area-Delay Product (used logic area + routing)',
        'clb_avg_util': '% of CLB used, average',
        'flutS.ff': 'Non-arithmetic Register Count',
        'arithmetic.ff': 'Arithmetic Register Count',
        'ff': 'Total Register Count',
    },
    # verbose=True,
    # merge_designs=True
)