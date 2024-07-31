import runs.kratos as kratos
from structure.run import Runner

runner = Runner()

# add all experiments
# kratos.explore_conv_1d_fu(runner)
kratos.explore_conv_1d_pw(runner, exp_root_dir='conv_1d/pw_v2') # conv1d-PW-S

results = runner.run_all_threaded(
    desc='run_exploration',
    num_parallel_tasks=4,
    filter_params=kratos.FILTER_PARAMS,
    filter_results=kratos.FILTER_RESULTS
)

for k, v in results.items():
    v.to_csv(f"{k.replace('/', '_')}_results.csv")