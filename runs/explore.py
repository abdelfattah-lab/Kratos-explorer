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
from copy import deepcopy

FILTER_PARAMS = ['ble_count', 'lut_size', 'sparsity', 'data_width']
FILTER_RESULTS = ['fmax', 'cpd', 'rcw', 'blocks', 'clb', 'adder']

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

def _add_to_runner(runner: Runner, exp_root_dir: str, design: Design, design_params: dict[str, any]) -> None:
    """
    Add the BASE_PARAMS provided for a given design and its parameters to a runner.
    """
    params = deepcopy(BASE_PARAMS)
    params[keys.KEY_EXP] |= {
        'root_dir': path.join('experiments', exp_root_dir)
    }
    params[keys.KEY_DESIGN] |= design_params

    runner.add_experiments(VtrExperiment, ARCH, design, params)

def explore_conv_1d_fu(runner: Runner, exp_root_dir: str = 'conv_1d/fu', is_L: bool = False):
    """
    Add Conv-1D Fully-Unrolled exploration to a Runner.
    """
    d = 16 if is_L else 8
    return _add_to_runner(runner, exp_root_dir, Conv1dFuDesign(), {
        'img_w': 32,
        'img_d': d,
        'fil_w': 3,
        'res_d': d,
        'stride_w': 1
    })

def explore_conv_1d_pw(runner: Runner, exp_root_dir: str = 'conv_1d/pw', is_L: bool = False):
    """
    Add Conv-1D Pixel-Wise exploration to a Runner.
    """
    return _add_to_runner(runner, exp_root_dir, Conv1dPwDesign(), {
        'img_w': 32,
        'img_d': 64,
        'fil_w': 3,
        'res_d': 128 if is_L else 64,
        'stride_w': 1
    })

def explore_conv_2d_fu(runner: Runner, exp_root_dir: str = 'conv_2d/fu', is_L: bool = False):
    """
    Add Conv-2D Fully-Unrolled exploration to a Runner.
    """
    d = 8 if is_L else 4
    return _add_to_runner(runner, exp_root_dir, Conv2dFuDesign(), {
        'img_w': 8,
        'img_h': 8,
        'img_d': d,
        'fil_w': 3,
        'fil_h': 3,
        'res_d': d,
        'stride_w': 1,
        'stride_h': 1
    })

def explore_conv_2d_rp(runner: Runner, exp_root_dir: str = 'conv_2d/rp', is_L: bool = False):
    """
    Add Conv-2D Row-Parallel exploration to a Runner.
    """
    d = 16 if is_L else 8
    return _add_to_runner(runner, exp_root_dir, Conv2dRpDesign(), {
        'img_w': 8,
        'img_h': 8,
        'img_d': d,
        'fil_w': 3,
        'fil_h': 3,
        'res_d': d,
        'stride_w': 1,
        'stride_h': 1
    })

def explore_conv_2d_pw(runner: Runner, exp_root_dir: str = 'conv_2d/pw', is_L: bool = False):
    """
    Add Conv-2D Pixel-Wise exploration to a Runner.
    """
    return _add_to_runner(runner, exp_root_dir, Conv2dPwDesign(), {
        'img_w': 25,
        'img_h': 25,
        'img_d': 64 if is_L else 32,
        'fil_w': 3,
        'fil_h': 3,
        'res_d': 64,
        'stride_w': 1,
        'stride_h': 1
    })