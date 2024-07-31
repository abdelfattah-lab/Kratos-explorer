import runs.kratos_mini as mini
from structure.run import Runner
from util.plot import plot_xy

runner = Runner()

# add experiments
# mini.explore_conv_1d_fu(runner) # mini conv1d-FU
mini.explore_conv_1d_pw(runner) # mini conv1d-PW
# ...and others

results = runner.run_all_threaded(
    desc='run_mini',
    num_parallel_tasks=8,
    filter_params=mini.FILTER_PARAMS,
    filter_results=mini.FILTER_RESULTS
)

for root_dir, df in results.items():
    filesafe_name = f"{root_dir.replace('/', '_')}_results"
    plot_xy(df, ['lut_size'], 'ble_count', 'fmax', subplots_identifiers=['sparsity', 'data_width'], y_axis_col_secondary='clb', save_path=f"{filesafe_name}.png")
    df.to_csv(f"{filesafe_name}.csv")