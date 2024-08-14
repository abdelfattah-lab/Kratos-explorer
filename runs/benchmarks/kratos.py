"""
Experiments to simulate Kratos benchmarks.
"""

from runs.benchmarks import get_params

def get_conv_1d_fu_params(base_params: dict[str, any], exp_root_dir: str = 'conv_1d/fu', is_L: bool = False) -> dict[str, any]:
    """
    Add Conv-1D Fully-Unrolled parameters.
    """
    d = 16 if is_L else 8
    return get_params(base_params, exp_root_dir, {
        'img_w': 32,
        'img_d': d,
        'fil_w': 3,
        'res_d': d,
        'stride_w': 1
    })

def get_conv_1d_pw_params(base_params: dict[str, any], exp_root_dir: str = 'conv_1d/pw', is_L: bool = False) -> dict[str, any]:
    """
    Add Conv-1D Pixel-Wise parameters.
    """
    return get_params(base_params, exp_root_dir, {
        'img_w': 32,
        'img_d': 64,
        'fil_w': 3,
        'res_d': 128 if is_L else 64,
        'stride_w': 1
    })

def get_conv_2d_fu_params(base_params: dict[str, any], exp_root_dir: str = 'conv_2d/fu', is_L: bool = False) -> dict[str, any]:
    """
    Add Conv-2D Fully-Unrolled parameters.
    """
    d = 8 if is_L else 4
    return get_params(base_params, exp_root_dir, {
        'img_w': 8,
        'img_h': 8,
        'img_d': d,
        'fil_w': 3,
        'fil_h': 3,
        'res_d': d,
        'stride_w': 1,
        'stride_h': 1
    })

def get_conv_2d_rp_params(base_params: dict[str, any], exp_root_dir: str = 'conv_2d/rp', is_L: bool = False) -> dict[str, any]:
    """
    Add Conv-2D Row-Parallel parameters.
    """
    d = 16 if is_L else 8
    return get_params(base_params, exp_root_dir, {
        'img_w': 8,
        'img_h': 8,
        'img_d': d,
        'fil_w': 3,
        'fil_h': 3,
        'res_d': d,
        'stride_w': 1,
        'stride_h': 1
    })

def get_conv_2d_pw_params(base_params: dict[str, any], exp_root_dir: str = 'conv_2d/pw', is_L: bool = False) -> dict[str, any]:
    """
    Add Conv-2D Pixel-Wise parameters.
    """
    return get_params(base_params, exp_root_dir, {
        'img_w': 25,
        'img_h': 25,
        'img_d': 64 if is_L else 32,
        'fil_w': 3,
        'fil_h': 3,
        'res_d': 64,
        'stride_w': 1,
        'stride_h': 1
    })

def get_gemmt_fu_params(base_params: dict[str, any], exp_root_dir: str = 'gemmt/fu', is_L: bool = False) -> dict[str, any]:
    """
    Add GEMM-T Fully-Unrolled parameters.
    """
    size = 32 if is_L else 16
    return get_params(base_params, exp_root_dir, {
        'row_num': size,
        'col_num': size,
        'length': size
    })

def get_gemmt_rp_params(base_params: dict[str, any], exp_root_dir: str = 'gemmt/rp', is_L: bool = False) -> dict[str, any]:
    """
    Add GEMM-T Fully-Unrolled parameters.
    """
    size = 128 if is_L else 32
    return get_params(base_params, exp_root_dir, {
        'row_num': size,
        'col_num': size,
        'length': size
    })

def get_gemms_params(base_params: dict[str, any], exp_root_dir: str = 'gemms', is_L: bool = False) -> dict[str, any]:
    """
    Add GEMM-S parameters.
    """
    size = 128 if is_L else 16
    return get_params(base_params, exp_root_dir, {
        'row_num': size,
        'col_num': size,
        'length': size
    })