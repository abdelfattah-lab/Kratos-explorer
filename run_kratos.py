import runs.kratos as kratos
from structure.run import Runner
from util.plot import plot_xy

runner = Runner()

# add all experiments
# kratos.explore_conv_1d_fu(runner) # conv1d-FU-S/L
kratos.explore_conv_1d_pw(runner) # conv1d-PW-S/L
# ... and others

results = runner.run_all_threaded(
    desc='run_exploration',
    num_parallel_tasks=4,
    filter_params=kratos.FILTER_PARAMS,
    filter_results=kratos.FILTER_RESULTS
)

for root_dir, df in results.items():
    filesafe_name = f"{root_dir.replace('/', '_')}_results"
    plot_xy(df, ['lut_size'], 'ble_count', 'fmax', subplots_identifiers=['sparsity', 'data_width'], y_axis_col_secondary='clb', save_path=f"{filesafe_name}.png")
    df.to_csv(f"{filesafe_name}.csv")