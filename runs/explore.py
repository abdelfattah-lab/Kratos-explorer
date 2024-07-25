import structure.consts.keys as keys
from impl.arch.base_exp import BaseExpArchFactory
from impl.design.conv_1d.fu import Conv1dFuDesign
from impl.design.conv_1d.pw import Conv1dPwDesign
from impl.design.conv_2d.fu import Conv2dFuDesign
from impl.design.conv_2d.rp import Conv2dRpDesign
from impl.design.conv_2d.pw import Conv2dPwDesign
from impl.exp.vtr import VtrExperiment
from structure.run import Runner
from structure.design import Design

import os.path as path
import pandas as pd
from copy import deepcopy

FILTER_PARAMS = ['ble_count', 'lut_size', 'sparsity', 'data_width']
FILTER_RESULTS = ['fmax', 'cpd', 'rcw', 'blocks', 'clb']

ARCH = BaseExpArchFactory()
BASE_PARAMS = {
    keys.KEY_EXP: {
        'verilog_search_dir': path.join(path.dirname(path.realpath(__file__)), '../verilog')
    },
    keys.KEY_ARCH: {
        'ble_count': [10, 15, 20, 25, 30],
        'lut_size': [3, 4, 5, 6]
        # 'lut_size': 5
    },
    keys.KEY_DESIGN: {
        # 'sparsity': 0,
        # 'data_width': 8
        'sparsity': [0, 0.5, 0.9],
        'data_width': [4, 8]
    }
}

def _explore_design_vtr(exp_root_dir: str, design: Design, design_params: dict[str, any]) -> pd.DataFrame:
    """
    Explore the BASE_PARAMS provided for a given design and its parameters.
    """
    params = deepcopy(BASE_PARAMS)
    params[keys.KEY_EXP] |= {
        'root_dir': path.join('experiments', exp_root_dir)
    }
    params[keys.KEY_DESIGN] |= design_params

    runner = Runner(ARCH, design, VtrExperiment, params)
    return runner.run_all_threaded(
        desc=exp_root_dir,
        num_parallel_tasks=12,
        filter_params=FILTER_PARAMS,
        filter_results=FILTER_RESULTS
    )

def explore_conv_1d_fu():
    """
    Explore Conv-1D Fully-Unrolled.
    """
    return _explore_design_vtr('conv_1d/fu', Conv1dFuDesign(), {
        'img_w': 8,
        'img_d': 8,
        'fil_w': 3,
        'res_d': 8,
        'stride_w': 1
    })

def explore_conv_1d_pw():
    """
    Explore Conv-1D Pixel-Wise.
    """
    return _explore_design_vtr('conv_1d/pw', Conv1dPwDesign(), {
        'img_w': 32,
        'img_d': 32,
        'fil_w': 3,
        'res_d': 64,
        'stride_w': 1
    })

def explore_conv_2d_fu():
    """
    Explore Conv-2D Fully-Unrolled.
    """
    return _explore_design_vtr('conv_2d/fu', Conv2dFuDesign(), {
        'img_w': 8,
        'img_h': 8,
        'img_d': 8,
        'fil_w': 3,
        'fil_h': 3,
        'res_d': 8,
        'stride_w': 1,
        'stride_h': 1
    })

def explore_conv_2d_rp():
    """
    Explore Conv-2D Row-Parallel.
    """
    return _explore_design_vtr('conv_2d/rp', Conv2dRpDesign(), {
        'img_w': 8,
        'img_h': 8,
        'img_d': 8,
        'fil_w': 3,
        'fil_h': 3,
        'res_d': 8,
        'stride_w': 1,
        'stride_h': 1
    })

def explore_conv_2d_pw():
    """
    Explore Conv-2D Pixel-Wise.
    """
    return _explore_design_vtr('conv_2d/pw', Conv2dPwDesign(), {
        'img_w': 25,
        'img_h': 25,
        'img_d': 32,
        'fil_w': 3,
        'fil_h': 3,
        'res_d': 64,
        'stride_w': 1,
        'stride_h': 1
    })