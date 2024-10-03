from structure.arch import ArchFactory
from structure.design import Design
from structure.exp import Experiment
from structure.consts.shared_defaults import DEFAULTS_EXP_QUARTUS
from structure.consts.shared_requirements import REQUIRED_KEYS_EXP
from util.extract import extract_info_quartus
from util.flow import start_dependent_process

import os

class QuartusExperiment(Experiment):
    def __init__(self, arch: ArchFactory, design: Design, params: dict[str, dict[str, any]]) -> None:
        super().__init__(arch, design, params)
        self.name = 'quartus'

    def run(self) -> None:
        """
        Run on Quartus.
        """
        self._prerun_check()

        # generic experiment setup
        self._setup_exp(DEFAULTS_EXP_QUARTUS, REQUIRED_KEYS_EXP)

        # generate wrapper file
        wrapper_file_name = 'design.v'
        with open(os.path.join(self.exp_dir, wrapper_file_name), 'w') as f:
            f.write(self.design.gen_wrapper(**self.design_params))

        # generate tcl/sdc files
        tcl_file_name = 'flow.tcl'
        with open(os.path.join(self.exp_dir, tcl_file_name), 'w') as tcl_file:
            tcl_file.write(self.design.gen_tcl(wrapper_file_name, **self.design_params))
        sdc_file_name = 'flow.sdc'
        with open(os.path.join(self.exp_dir, sdc_file_name), 'w') as sdc_file:
            sdc_file.write(self.design.gen_sdc(**self.design_params))

        # Make out and error files
        self.stdout_file = open(os.path.join(self.exp_dir, self.exp_params['stdout_file']), 'w')
        self.stderr_file = open(os.path.join(self.exp_dir, self.exp_params['stderr_file']), 'w')

        # Define Quartus command
        cmd = ['quartus_sh', '-t', tcl_file_name]
        
        # start Quartus on subprocess        
        self.process = start_dependent_process(cmd, stdout=self.stdout_file, stderr=self.stderr_file, cwd=self.exp_dir)

        # start GC thread
        self._start_gc_thread(self._clean, ())

    def get_result(self, **kwargs) -> dict:
        self._preresult_check()

        self.result = extract_info_quartus(os.path.join(self.exp_dir, 'output'), **kwargs)
        return self.result