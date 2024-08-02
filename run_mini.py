import runs.kratos_mini as mini
from structure.run import Runner
from util.plot import plot_xy
from util.results import save_and_plot
from os.path import join

runner = Runner()

# add experiments
# mini.explore_conv_1d_fu(runner) # mini conv1d-FU
mini.explore_conv_1d_pw(runner) # mini conv1d-PW
# ...and others

results = runner.run_all_threaded(
    desc='run_mini',
    num_parallel_tasks=8,
    filter_params=mini.FILTER_PARAMS,
    filter_results=mini.FILTER_RESULTS,
    allow_skipping=True,
    avoid_mult=True
)

def plot_fn(save_dir, filesafe_name, df):
    save_path = join(save_dir, f"{filesafe_name}" + "_ble_{col}.png")
    for col in ['fmax', 'clb']:
        # plot_xy(df, ['sparsity'], 'lut_size', col, subplots_identifiers=['data_width'], save_path=save_path)
        plot_xy(df, ['lut_size'], 'ble_count', col, subplots_identifiers=['sparsity', 'data_width'], save_path=save_path.format(col=col))

save_and_plot(results, plot_fn)