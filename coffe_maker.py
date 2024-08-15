"""
This is a tool to generate a batch of COFFE input files for each permutation of architecture parameters.
"""

# Logging functions
def log(message: str) -> None:
    print(f"(!) {message}")
def log_error(message: str) -> None:
    print(f"[ERR] {message}")

import argparse
import os
import itertools
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--arch_module', help="ArchFactory module to use. Currently supported: gen_exp", default='gen_exp')
parser.add_argument('-p', '--params_file', help="file containing newline separated parameters, intended for the ArchFactory. Each line should have <param>=<value_1>,<value_2>,... e.g., lut_size=3,4,5. You can also specify an integer range, e.g., lut_size=3-6,8")
parser.add_argument('-o', '--output_dir', help="output directory to put new files in; created for you", default='coffe_maker_out')
parser.add_argument('-r', '--record_filename', help="name of the record file generated in the output directory", default='record')
args = parser.parse_args()

params_file_path = args.params_file
if params_file_path is None or not os.path.exists(params_file_path):
    log_error("Please provide a valid parameter file with -p (or --params_file).")
    exit()

# get architecture
arch = None
if args.arch_module == 'gen_exp':
    from impl.arch.gen_exp import GenExpArchFactory
    arch = GenExpArchFactory()
else:
    log_error(f"arch_module {args.arch_module} is not recognized.")
    exit()

# parse parameter file
params_dict = {}
with open(params_file_path, 'r') as pf:
    for i, line in enumerate(pf.readlines()):
        def report_error(message):
            log_error(f"Error on line {i+1} of {params_file_path}: {message}")
            exit()

        line_split = line.strip().split('=')
        if len(line_split) != 2:
            report_error(f"not in recognizable format. (require <param>=<values>, got: {line})")

        param = line_split[0].strip()
        vals = line_split[1].strip().split(',')
        params_dict[param] = []

        for val in vals:
            val = val.strip()
            if '-' in val:
                # treat as range if possible
                val_split = val.split('-')
                if len(val_split) == 2:
                    l, r = val_split
                    try:
                        [params_dict[param].append(x) for x in range(int(l), int(r) + 1)]
                        continue
                    except:
                        pass
            try:
                # integer pass
                val = int(val)
            except:
                try:
                    # float pass
                    val = float(val)
                except:
                    pass
            
            params_dict[param].append(val)

log(f"Read the following parameters: {params_dict}")

# Generate all permutations
keys = params_dict.keys()
values = params_dict.values()

permutations = [dict(zip(keys, combination)) for combination in itertools.product(*values)]

# make directory and write
os.makedirs(args.output_dir, exist_ok=True)
records = []
for i, p in enumerate(permutations):
    params = arch.verify_params(p)
    filename = f"{args.arch_module}_{arch.get_name(**params)}.txt"
    records.append({**params, 'coffe_filename': filename})

    filename = os.path.join(args.output_dir, filename)
    with open(filename, 'w') as f:
        f.write(arch.get_coffe_input_file(**params))
        log(f"Wrote {filename}.")

pd.DataFrame.from_records(records).to_csv(os.path.join(args.output_dir, f'{args.record_filename}.csv'))
log(f"Finished {len(permutations)} file(s).")