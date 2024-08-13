import runs.kratos_mini as mini
from structure.run import Runner
from util.calc import normalize_df
from util.plot import plot_xy
from util.results import save_and_plot
from os.path import join

runner = Runner()

# add experiments
# mini.explore_conv_1d_fu(runner) # mini conv1d-FU
# mini.explore_conv_1d_pw(runner) # mini conv1d-PW
# mini.explore_conv_2d_fu(runner) # mini conv2d-FU
# mini.explore_conv_2d_rp(runner) # mini conv2d-RP
# mini.explore_conv_2d_pw(runner) # mini conv2d-PW
# mini.explore_gemmt_fu(runner) # mini gemmt-FU
# ...and others

results = runner.run_all_threaded(
    desc='run_mini',
    num_parallel_tasks=8,
    filter_params=mini.FILTER_PARAMS,
    filter_results=mini.FILTER_RESULTS,
    allow_skipping=True,
    avoid_mult=True
)

def df_mod_fn(df):
    # average CLB utilization
    df['clb_avg_util'] = df.apply(lambda row: row['fle'] / row['clb'] / row['ble_count'], axis=1)
    return df
    
def grp_mod_fn(df):
    # rough ADP
    extracted = df[['cpd', 'clb', 'ble_count']].copy(deep=True)
    extracted['total_area'] = extracted.apply(lambda row: row['clb'] * row['ble_count'], axis=1)
    normalize_df(extracted, cols=['cpd', 'total_area'], min_max_vals=(1, 2))
    df['adp'] = extracted.apply(lambda row: row['cpd'] * row['total_area'], axis=1)
    normalize_df(df, norm_type='min-max', cols=['adp']) # normalize
    return df

def plot_fn(save_dir, filesafe_name, df):
    save_path = join(save_dir, f"{filesafe_name}" + "_{x_axis}_{col}.png")
    short_labels = dict(lut_size='K', CLB_groups_per_xb='xb', sparsity='s', data_width='d', ble_count='N')
    for col in ['adp', 'fmax', 'clb', 'clb_avg_util', 
                #'fle', 'adder'
    ]:
        x_axis_list = ['ble_count', 'CLB_groups_per_xb']
        # plot_xy(df, ['lut_size'], x_axis_list, col, subplots_identifiers=['sparsity', 'data_width'], save_path=save_path.format(x_axis='_'.join(x_axis_list), col=col), short_labels=short_labels)
        for x_axis in x_axis_list:
            plot_xy(df, ['lut_size'], x_axis, col, 
                subplots_identifiers=[*[a for a in x_axis_list if a != x_axis], 'sparsity', 'data_width'], 
                subplots_df_modifier=grp_mod_fn,
                save_path=save_path.format(x_axis=x_axis, col=col), 
                short_labels=short_labels
            )

save_and_plot(results, df_mod_fn=df_mod_fn, plot_fn=plot_fn)