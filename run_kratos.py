import runs.kratos as kratos
from structure.run import Runner
from util.plot import plot_xy
from util.results import save_and_plot
from os.path import join

runner = Runner()

# add all experiments
# kratos.explore_conv_1d_fu(runner) # conv1d-FU-S/L
kratos.explore_conv_1d_pw(runner) # conv1d-PW-S/L
# ... and others

results = runner.run_all_threaded(
    desc='run_exploration',
    num_parallel_tasks=4,
    filter_params=kratos.FILTER_PARAMS,
    filter_results=kratos.FILTER_RESULTS,
    avoid_mult=True
)

def plot_fn(save_dir, filesafe_name, df):
    save_path = join(save_dir, f"{filesafe_name}" + "_ble_{col}.png")
    for col in ['fmax', 'clb']:
        # plot_xy(df, ['sparsity'], 'lut_size', col, subplots_identifiers=['data_width'], save_path=save_path)
        plot_xy(df, ['lut_size'], 'ble_count', col, subplots_identifiers=['sparsity', 'data_width'], save_path=save_path.format(col=col))

save_and_plot(results, plot_fn=plot_fn)