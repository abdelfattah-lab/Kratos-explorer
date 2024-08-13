from structure.exp import Experiment, ExperimentFactory
from structure.arch import ArchFactory
from structure.design import Design
from util.formatting import pretty, gen_time_elapsed

import os
from timeit import default_timer as timer
from typing import Type, TypeVar
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import traceback

E = TypeVar('E', bound=Experiment)
class Runner():
    """
    Runs a list of Experiments as generated by an ExperimentFactory.
    """
    def __init__(self):
        """
        Prepare the Runner to accept new experiments via add_experiments().
        """
        self.factory = ExperimentFactory()
        self.experiments: list[E] = []

    def add_experiments(self, experiment_class: Type[E], arch: ArchFactory, design: Design, params: dict[str, any]):
        """
        Add experiments to the Runner's list. All experiments will be threaded by the same ThreadPoolExecutor.

        Required arguments:
        * experiment_class:Type[Experiment], concrete Experiment class to use
        * arch:ArchFactory, concrete ArchFactory to use
        * design:Design, concrete Design to use
        * params:dict, parameters to use
        """
        self.experiments += self.factory.gen_experiments(experiment_class, arch, design, params)

    def run_all_threaded(self,
            verbose: bool = False,
            track_run_time: bool = True,
            desc: str = 'run', 
            num_parallel_tasks: int = 1,
            runner_err_file: str = 'runner.err',
            results_status_key: str = 'status',
            filter_params: list[str] = None,
            filter_results: list[str] = None,
            **kwargs
        ) -> dict[str, pd.DataFrame]:
        """
        Main function: run all generated experiments with a thread pool.

        Optional arguments:
        * verbose:bool, prints detailed report of each result if True. Default: False
        * track_run_time:bool, will track total run time and print at the end if True. Default: True
        * desc:str, description of run
        * num_parallel_tasks:int, maximum number of simultaneous threads allowed in the thread pool.
        * runner_err_file:str, name of error file created by runner if an exception occurs while running the Experiment. Created in the Experiment folder.
        * results_status_key:str, key in results dictionary from the Experiment that should yield a True/False value, indicating success/failure. Default: 'status'
        * filter_params:list[str], a list of parameter keys that should be extracted from the Experiment parameters and included in the resultant Dataframe. Pass None to include all. Default: None
        * filter_results:list[str], a list of result keys that should be extracted from the result and included in the resultant Dataframe. Pass None to include all. Default: None
        All other keyword arguments are passed directly to the Experiment.run() function.

        @returns a dictionary of (experiment root directory): (Pandas DataFrame with filtered parameters and results).
        """
        # print experiment count.
        total_count = len(self.experiments)
        print(f"Running '{desc}': Found {total_count} experiment(s).")

        # log start time.
        start_time = timer()
        exp_start_times = {}

        # runnable
        def run_experiment(exp: Experiment) -> tuple[dict, dict]:
            if track_run_time:
                # log start time of experiment
                nonlocal exp_start_times
                exp_start_times[exp] = timer()

            exp.run(**kwargs)
            exp.wait()
            return exp.get_full_params(), exp.get_result()
        
        # submit all Experiments into the ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=num_parallel_tasks)
        futures_dict = { executor.submit(run_experiment, exp): exp for exp in self.experiments }

        # track successes
        successes = 0

        # collect all results
        results = {}
        def add_to_results(res_dict: dict[str, any], search_dict: dict[str, any], keys: list[str]):
            """
            Recursively search a nested dictionary and add required leaf keys to a result dictionary.
            """
            for k, v in search_dict.items():
                if isinstance(v, dict):
                    add_to_results(res_dict, v, keys)
                elif keys is None or k in keys:
                    res_dict[k] = v

        for i, future in enumerate(as_completed(futures_dict.keys())):
            exp: Experiment = futures_dict[future]
            try:
                result = future.result()
                inp, out = result

                # search for required keys and add to results
                res_dict = {}
                add_to_results(res_dict, inp, filter_params)
                add_to_results(res_dict, out, filter_results)

                is_success = out.get(results_status_key, False)
                if is_success:
                    successes += 1

                if exp.root_dir in results:
                    results[exp.root_dir].append(res_dict)
                else:
                    results[exp.root_dir] = [res_dict]
                
                if verbose:
                    print("====================================")
                    print(f"Result {i+1}/{total_count}: {'succeeded' if is_success else 'failed'}")
                    if track_run_time:
                        print(f" (Time elapsed for this experiment: {gen_time_elapsed(timer() - exp_start_times[exp])})")
                    
                    print(f"@ root directory {exp.root_dir}")
                    pretty(res_dict, 1)
                    print("====================================")
                else:
                    print(f"Progress: {i+1}/{total_count} complete ({successes} succeeded)", end='\r', flush=True)
                                
            except Exception as e:
                err_str = f"Exception:\n{traceback.format_exc()}\n"
                with open(os.path.join(exp.exp_dir, runner_err_file), 'w') as f:
                    f.write(err_str)
                
                if verbose:
                    print("!-----------------------------------")
                    print(f"For experiment with directory {exp.exp_dir}, an exception occurred:")
                    print(err_str)
                    print("------------------------------------")
            
        executor.shutdown()

        # print summary
        top_line = f"*********************** Run '{desc}' complete! ***********************"
        print(top_line)
        print(f"Total: {total_count}, of which {successes} succeeded ({(successes / total_count * 100):.2f}%).")
        if track_run_time:
            print(f"Run time: {gen_time_elapsed(timer() - start_time)}.")
        print("*" * len(top_line))

        return { k: pd.DataFrame.from_records(v) for k, v in results.items() }