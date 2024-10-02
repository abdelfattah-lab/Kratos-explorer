from structure.exp import Experiment
from structure.consts.shared_defaults import DEFAULTS_EXP_VTR
from structure.consts.shared_requirements import REQUIRED_KEYS_EXP
from util.extract import extract_info_vtr
from util.flow import start_dependent_process

import os
import subprocess

class VtrExperiment(Experiment):
    """
    VTR implementation of an Experiment.
    """

    def run(self) -> None:
        """
        Run on VTR.

        dry_run: if True, only generate files, do not run VTR
        clean: if True, zip the temp files after VTR finishes to save space
        ending: ending stage of VTR, if None, run the whole flow, options: 'parmys', 'vpr'
        seed: random seed for VTR
        allow_skipping: if True, then the experiment is skipped if the folder already exists with valid results
        adder_cin_global: tells VTR to connect the first cin of an adder/subtractor chain to (True) global GND/Vdd, or (False) a dummy adder. Default: False
        soft_multiplier_adders: tells VTR to use cascading adder chains if True, else a compressor tree, to implement soft multiplication. Default: False
        avoid_mult: if True, then avoids using hard multipliers. Default: False
        force_denser_packing: if True, then force VPR to pack as tightly as possible. Default: False
        """
        self._prerun_check()
        
        # get variables
        dry_run = self.exp_params.get('dry_run', False)
        allow_skipping = self.exp_params.get('allow_skipping', False)

        # generic experiment setup
        self._setup_exp(DEFAULTS_EXP_VTR, REQUIRED_KEYS_EXP, clear_exp_dir=not allow_skipping)

        # Check for viable result (i.e., it has been run in the past)
        if (not dry_run) and allow_skipping and self.get_result().get('status', False):
            return
        
        # get variables
        clean = self.exp_params.get('clean', True)
        ending = self.exp_params['ending']
        seed = self.exp_params['seed']
        adder_cin_global = self.exp_params.get('adder_cin_global', False)
        soft_multiplier_adders = self.exp_params.get('soft_multiplier_adders', False)
        avoid_mult = self.exp_params.get('avoid_mult', False)
        force_denser_packing = self.exp_params.get('force_denser_packing', False)

        # generate wrapper file
        wrapper_file_name = 'design.v'
        with open(os.path.join(self.exp_dir, wrapper_file_name), 'w') as f:
            f.write(self.design.gen_wrapper(**self.design_params))

        # generate architecture file
        arch_file_name = 'arch.xml'
        with open(os.path.join(self.exp_dir, arch_file_name), 'w') as f:
            f.write(self.arch.get_arch(**self.arch_params))

        if dry_run:
            print(f"""(!) Created under {self.exp_dir}:
- README file: {self.readme_file_name}
- Wrapper file: {wrapper_file_name}
- Architecture file: {arch_file_name}
>>> Dry run completed.""")
            return

        # Find VTR and define command
        vtr_root = os.environ.get('VTR_ROOT')
        if vtr_root is None:
            raise RuntimeError('VTR_ROOT not found in environment variables; unable to execute VTR.')
        vtr_script_path = os.path.join(vtr_root, 'vtr_flow/scripts/run_vtr_flow.py')
        cmd = ['python', vtr_script_path, wrapper_file_name, arch_file_name,
               '-parser', 'system-verilog', '-top', self.design.wrapper_module_name, '-search', self.verilog_search_dir, '--seed', str(seed)]
        if adder_cin_global:
            cmd += ['-adder_cin_global'] # only works with self-modified fork: https://github.com/abdelfattah-lab/vtr-updated
        if soft_multiplier_adders:
            cmd += ['-soft_multiplier_adders'] # only works with self-modified fork: https://github.com/abdelfattah-lab/vtr-updated
        if avoid_mult:
            cmd += ['-min_hard_mult_size', '9999'] # arbitrarily large multiplier size
        if ending is not None:
            cmd += ['-ending_stage', ending]

        # Add VPR commands
        if force_denser_packing:
            # focus solely on area
            cmd += ['--alpha_clustering', '0']

            # focus solely on signal sharing
            cmd += ['--connection_driven_clustering', 'on'] 
            cmd += ['--beta_clustering', '0']

        # Make out and error files
        self.stdout_file = open(os.path.join(self.exp_dir, self.exp_params['stdout_file']), 'w')
        self.stderr_file = open(os.path.join(self.exp_dir, self.exp_params['stderr_file']), 'w')

        # start VTR on subprocess        
        self.process = start_dependent_process(cmd, stdout=self.stdout_file, stderr=self.stderr_file, cwd=self.exp_dir)

        # start GC thread
        self._start_gc_thread(self._clean, (clean,))

    def _clean(self, clean=True) -> None:
        """
        VTR cleanup with zipping of large files.
        """
        super()._clean()
        if not clean:
            return
        
        output_temp_dir = os.path.join(self.exp_dir, 'temp')

        # zip parmys.out and delete the original file
        # using subprocess to zip the file
        possible_list = ['parmys.out', 'design.net.post_routing', 'design.net', 'design.route']
        remove_list = []

        for possible in possible_list:
            if os.path.exists(os.path.join(output_temp_dir, possible)):
                remove_list.append(possible)

        cmd = ['zip', '-r', 'largefile.zip'] + remove_list

        try:
            zip_result = subprocess.run(cmd, cwd=output_temp_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if zip_result.returncode == 0:
                for remove_file in remove_list:
                    remove_path = os.path.join(output_temp_dir, remove_file)
                    if os.path.exists(remove_path):
                        os.remove(remove_path)
            else:
                print(f"Unable to perform zipping for: {output_temp_dir}")
        except:
            print(f"Unable to perform zipping for: {output_temp_dir}")

    def get_result(self, **kwargs) -> dict:
        """
        Get result of VTR run.
        """
        self._preresult_check()

        self.result = extract_info_vtr(os.path.join(self.exp_dir, 'temp'), **kwargs)
        return self.result

