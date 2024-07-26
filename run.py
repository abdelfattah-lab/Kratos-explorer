import runs.explore as expl
from structure.run import Runner

runner = Runner()

# add all experiments
# expl.explore_conv_1d_fu(runner)
expl.explore_conv_1d_pw(runner)

results = runner.run_all_threaded(
    desc='run_exploration',
    num_parallel_tasks=3,
    filter_params=expl.FILTER_PARAMS,
    filter_results=expl.FILTER_RESULTS
)

for k, v in results.items():
    v.to_csv(f'{k.replace('/', '_')}_results.csv')