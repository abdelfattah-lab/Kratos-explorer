from structure.exp import Experiment, ExperimentFactory
from structure.arch import ArchFactory
from structure.design import Design
from util import pretty

import os
from timeit import default_timer as timer
from typing import Type, TypeVar
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

E = TypeVar('E', bound=Experiment)
class Runner():
    """
    Runs a list of Experiments as generated by an ExperimentFactory.
    """
    def __init__(self, arch: ArchFactory, design: Design, experiment_class: Type[E], params: dict[str, any]):
        """
        Generate all experiments.
        """
        self.factory = ExperimentFactory(arch, design, experiment_class)
        self.experiments = self.factory.gen_experiments(params)

    def run_all_threaded(self,
            track_run_time: bool = True,
            desc: str = 'run', 
            num_parallel_tasks: int = 1, 
            runner_err_file: str = 'runner.err',
            filter_params: list[str] = None,
            filter_results: list[str] = None,
            **kwargs
        ) -> pd.DataFrame:
        """
        Main function: run all generated experiments with a thread pool.

        Optional arguments:
        * track_run_time:bool, will track total run time and print at the end if True. Default: True
        * desc:str, description of run
        * num_parallel_tasks:int, maximum number of simultaneous threads allowed in the thread pool.
        * runner_err_file:str, name of error file created by runner if an exception occurs while running the Experiment. Created in the Experiment folder.
        * filter_params:list[str], a list of parameter keys that should be extracted from the Experiment parameters and included in the resultant Dataframe. Pass None to include all. Default: None
        * filter_results:list[str], a list of result keys that should be extracted from the result and included in the resultant Dataframe. Pass None to include all. Default: None
        All other keyword arguments are passed directly to the Experiment.run() function.

        @return a Pandas DataFrame with filtered parameters and results.
        """
        # print experiment count.
        total_count = len(self.experiments)
        print(f"Running '{desc}': Found {total_count} experiment(s).")

        # log start time.
        start_time = timer()

        # runnable
        def run_experiment(exp: Experiment) -> dict:
            exp.run(**kwargs)
            exp.wait()
            return exp.get_full_params(), exp.get_result()
        
        # submit all Experiments into the ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=num_parallel_tasks)
        futures_dict = { executor.submit(run_experiment, exp): exp for exp in self.experiments }

        # collect all results
        results = []
        def add_to_results(res_dict: dict[str, any], search_dict: dict[str, any], keys: list[str]):
            """
            Recursively search a nested dictionary and add required leaf keys to a result dictionary.
            """
            for k, v in search_dict.items():
                if isinstance(v, dict):
                    add_to_results(res_dict, v, keys)
                elif keys is None or k in keys:
                    res_dict[k] = v

        # track successes
        successes = 0

        for i, future in enumerate(as_completed(futures_dict.keys())):
            exp: Experiment = futures_dict[future]
            try:
                result = future.result()
                inp, out = result

                # search for required keys and add to results
                res_dict = {}
                add_to_results(res_dict, inp, filter_params)
                add_to_results(res_dict, out, filter_results)

                print("====================================")
                print(f"Result {i+1}/{total_count}")
                pretty(res_dict, 1)
                print("====================================")
                
                results.append(res_dict)
                successes += 1
            except Exception as e:
                err_str = f"Exception:\n{repr(e)}\n"
                with open(os.path.join(exp.exp_dir, runner_err_file), 'w') as f:
                    f.write(err_str)
                
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
            print(f"Run time: {(timer() - start_time):.3f} second(s).")
        print("*" * len(top_line))
        return pd.DataFrame.from_records(results)