import structure.consts.keys as keys
from impl.arch.base import BaseArchFactory
from impl.arch.gen_exp import GenExpArchFactory
from impl.exp.vtr import VtrExperiment
from structure.run import Runner
from structure.design import Design
from util.calc import merge_op
from util.results import save_and_plot
from util.plot import plot_xy

from typing import Type
import os.path as path
from os import sep
import pandas as pd
from copy import deepcopy

def run_vtr_denoised_v1(
        design_list: list[tuple[Type[Design], dict[str, any]]],
        variable_arch_params: dict[str, list[any]],
        filter_params_baseline: list[str],
        filter_params_baseline_short_labels: dict[str, str] = {},
        filter_results: list[str] = ['fmax', 'cpd', 'rcw', 'blocks', 'clb', 'fle', 'adder', 'mult_36'],
        seeds: tuple[int, int, int] = (1239, 5741, 1473),
        merge_designs: bool = False,
        **kwargs
    ) -> None:
    """
    Runs the following sequence:
    1. Runs all provided designs on v0 and v1 architecture on provided seeds.
    2. Averages results across all seeds for each architecture.
    3. Normalize v0 results as 1.0, and v1 results relative to v0. (Baseline normalization)
    4. Plots normalized results, and saves both baseline and normalized results to the default results folder, under the latest timestamp.

    Required arguments:
    * design_list:[(Design, params: dict[str, any]), ...], all the designs and their associated full base parameters. You can generate these parameters with the functions under `runs.benchmarks`.
    * variable_arch_params:dict[str, [...]], variable parameters that are added to the baseline architecture parameters, intended for the v1 architecture.
    * filter_params_baseline:[str, ...], parameters (non-architecture) that are varied and should be extracted into a DataFrame (e.g., sparsity, data width).
    
    Optional arguments:
    * filter_params_baseline_short_labels:dict[str, str], short translations for parameter keys (e.g., 'sparsity': 's').
    * filter_results:list[str], list of parameters to extract from VPR. All will be baseline normalized and plotted.
    * seeds: (int, int, int), a tuple of 3 seeds to use for averaging.
    * merge_designs:bool, will take the geometric mean of all designs as the final result if True, else each design is saved as its own separate experiment. Default: False
    """
    # x-axis is derived from variable architecture parameters
    filter_params_new = list(variable_arch_params.keys())
    
    # Sanity checks
    if len(filter_params_new) < 1 or len(filter_params_new) > 2:
        raise ValueError("filter_params_new must be of length of either 1 or 2!")

    # Ensure parameters for post-processing are present
    if 'ble_count' not in variable_arch_params.keys():
        raise ValueError("This sequence requires the architecture to have 'ble_count' as a variable!")
    if 'ble_count' not in filter_params_new:
        filter_params_new.append('ble_count')
    if 'cpd' not in filter_results:
        filter_results.append('cpd')
    if 'clb' not in filter_results:
        filter_results.append('clb')

    # Define variables
    runner = Runner()

    exp_types = {
        'baseline': BaseArchFactory(),
        'new': GenExpArchFactory()
    }
    exp_results = {
        'baseline': {},
        'new': {}
    }

    # Setup Runner
    runner = Runner()
    
    # add all experiments for all seeds
    for seed in seeds:
        for (design, params) in design_list:
            for exp_type, arch in exp_types.items():
                p = deepcopy(params)
                p[keys.KEY_EXP]['seed']  = seed
                p[keys.KEY_EXP]['root_dir'] = path.join(p[keys.KEY_EXP]['root_dir'], f"{exp_type}-{seed}")
                if exp_type != 'baseline':
                    p[keys.KEY_ARCH] |= variable_arch_params
                runner.add_experiments(VtrExperiment, arch, design, p)

    # run all experiments
    results = runner.run_all_threaded(
        filter_params=filter_params_baseline + filter_params_new,
        filter_results=filter_results,
        **kwargs
    )

    # process results
    for exp_dir, df in results.items():
        # process experiment directory
        exp_dir_split = exp_dir.split(sep)
        true_exp_dir = sep.join(exp_dir_split[:-1])
        exp_type, seed = exp_dir_split[-1].split('-')

        # add approximate CLB area and ADP
        df['clb_area'] = df['clb'] * (10 if exp_type == 'baseline' else df['ble_count'])
        df['adp'] = df['clb_area'] * df['cpd']

        # concatenate DataFrames (and take mean if complete)
        df_dict = exp_results[exp_type]
        if true_exp_dir not in df_dict:
            df_dict[true_exp_dir] = df
        else:
            df_dict[true_exp_dir] = pd.concat([df_dict[true_exp_dir], df], ignore_index=True)
    
    # add post-processing keys
    filter_results.append('clb_area') # approximate CLB area
    filter_results.append('adp')      # approximate ADP

    # take means of each DataFrame
    for exp_type, dfs in exp_results.items():
        # used if merge_designs is True
        merged = None

        for key, df in dfs.items():
            flt = filter_params_baseline.copy()
            if exp_type != 'baseline':
                flt += filter_params_new
            
            seed_mean = df.groupby(by=flt).mean().reset_index()
            if merge_designs:
                # merge all DataFrames into one DataFrame
                if merged is None:
                    merged = seed_mean.copy(deep=True)
                else:
                    # multiply columns
                    merged = merge_op(merged, seed_mean, lambda a, b: a * b, flt)
            else:
                # save DataFrame individually
                exp_results[exp_type][key] = seed_mean

        if merge_designs:
            # drop all other keys
            keys_to_drop = list(exp_results[exp_type].keys())
            for key in keys_to_drop:
                exp_results[exp_type].pop(key, None)
            
            # take the n-th root (geometric mean)
            for col in filter_results:
                merged[col] **= 1/(len(keys_to_drop))
            exp_results[exp_type]['merged'] = merged

    # baseline normalization and post-processing
    norm_results = exp_results['new']
    for key, df in norm_results.items():
        # perform merge and divide by baseline
        norm_results[key] = merge_op(df, exp_results['baseline'][key], lambda a, b: a / b, filter_params_baseline)

    # save baseline results
    def do_with_dir_fn(dir: str):
        for exp_dir, df in exp_results['baseline'].items():
            df.to_csv(path.join(dir, f"{exp_dir.replace(path.sep, '_')}_baseline_results.csv"))

    # define plot function
    def plot_fn(save_dir: str, filesafe_name: str, df: pd.DataFrame) -> None:
        plot_xy(df, filter_params_baseline, filter_params_new, filter_results, 
                save_path=path.join(save_dir, f"{filesafe_name}_graphs.png"),
                short_labels=filter_params_baseline_short_labels)
    
    # save into results directory
    save_and_plot(norm_results, do_with_dir_fn=do_with_dir_fn, plot_fn=plot_fn)