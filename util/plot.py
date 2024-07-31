"""
Convenience functions for plotting results.
"""

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
import math
from itertools import cycle
from random import shuffle

USABLE_MARKERS = ['.', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', '+', 'x', 'X', 'D']

DATA_WIDTH_DEFAULT = [1, 2, 4, 8]
SPARSITY_DEFAULT = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
COLOR_LIST_DEFAULT = [
    ['#fb6a4a', '#fcae91', '#d9181d'],
    ['#41b6c4', '#a1cac4', '#225ea8'],
    ['#74c476', '#bae4b3', '#238b45'],
    ['#fd8d3c', '#fdbe85', '#d94701'],
    ['#6baed6', '#bdd7e7', '#2171b5'],
    ['#78c679', '#c2e699', '#238443']
]

def plot_trend(mat_list: list[np.ndarray], labels: list[str], color_list=COLOR_LIST_DEFAULT, xlabel='', ylabel='', title='', save_name=''):
    assert len(mat_list) == len(labels)

    for idx in range(len(mat_list)):
        mat = mat_list[idx]
        label_name = labels[idx]
        data = mat / np.amax(mat, axis=0)
        # print(data)
        x_values = SPARSITY_DEFAULT

        # Calculate statistics
        means = np.mean(data, axis=1)
        lower_bound = np.min(data, axis=1)
        percentile_25 = np.percentile(data, 25, axis=1)
        # percentile_50 = np.percentile(data, 50, axis=1)
        percentile_75 = np.percentile(data, 75, axis=1)
        upper_bound = np.max(data, axis=1)

        # Plotting
        bar_width = 0.05

        transparency = 0.9

        for i, x in enumerate(x_values):
            plt.errorbar(x, means[i], yerr=[[means[i] - lower_bound[i]], [upper_bound[i] - means[i]]], color=color_list[idx][0], capsize=5, label='', alpha=transparency)
            plt.errorbar(x, means[i], yerr=[[means[i] - percentile_25[i]], [percentile_75[i] - means[i]]], elinewidth=10, color=color_list[idx][1], capsize=0, label='', alpha=transparency)

        # plot mean at top of the graph
        plt.plot(x_values, means, color=color_list[idx][2], label=label_name, linewidth=1, alpha=transparency)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    if (save_name is not None) and (save_name != ''):
        plt.savefig(save_name, dpi=600)

    # plt.show()
    plt.clf()
    plt.close()


def plot_result_3d(axis1, axis2, datapoints, description1='', description2='', description3='', title='', save_name='', elevation=25, azimuth=-145, alpha=1.0):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    _x = np.arange(len(axis1))
    _y = np.arange(len(axis2))
    _xx, _yy = np.meshgrid(_x, _y)
    x, y = _xx.ravel(), _yy.ravel()

    # Heights of bars are given by frequency
    datapoints = np.array(datapoints).T  # for unknown reason, datapoints is transposed, then it is correctly converted to 3d bar plot
    top = datapoints.ravel()
    bottom = np.zeros_like(top)

    # Change the width and depth here to make bars thinner
    width = depth = 0.5

    # Normalize to [0,1]
    norm = plt.Normalize(top.min(), top.max())

    # Create colormap
    colors = cm.Reds(norm(top))

    ax.bar3d(x, y, bottom, width, depth, top, color=colors, shade=True, edgecolor='black', alpha=alpha)
    ax.set_xticks(_x)
    ax.set_yticks(_y)
    ax.set_xticklabels(axis1)
    ax.set_yticklabels(axis2)
    ax.set_xlabel(description1)
    ax.set_ylabel(description2)
    ax.set_zlabel(description3)
    # Set the view angle
    ax.view_init(elev=elevation, azim=azimuth)
    ax.set_title(title)
    # save the figure in png with white background and high resolution
    if save_name != '':
        plt.savefig(save_name, bbox_inches='tight', pad_inches=1, transparent=False, dpi=600)

    plt.clf()
    plt.close(fig)

def plot_xy(
        df: pd.DataFrame, 
        group_identifiers: list[str], 
        x_axis_col: str, 
        y_axis_col: str, 
        subplots_identifiers: list[str] = None,
        y_axis_col_secondary: str = None,
        x_axis_label: str = None,
        y_axis_label: str = None, 
        y_axis_label_secondary: str = None, 
        save_path: str = None,
        ax: Axes = None
    ) -> None:
    """
    Plots a multi-line XY graph.

    Required arguments:
    * df:pandas.DataFrame, dataframe to use as data for plotting.
    * group_identifiers:list[str], Rows with the same group_identifiers values will be plot as a line.
    * x_axis_col:str, column to use as x-axis value for each line.
    * y_axis_col:str, column to use as left y-axis value for each line.

    Optional arguments:
    * subplots_identifiers:list[str], if provided, then subplots for each subset of unique values of the identifiers will be created, with the group identifiers applied for each.
    * y_axis_col_secondary:str, if provided, then a new line is created with this as right y-axis value. Default: None
    * *_axis_label*:str, provide the label to use for each axis. If None is provided, then it defaults to the column name. Default: None
    * save_name:str, if provided, then plot image is saved at the provided path; else the result is just displayed. Default: None
    """
    # Convenience function for labelling
    def get_identifiers_label(identifiers: list[str], values: list[str] = None, df: pd.DataFrame = None) -> str:
        assert values is not None or df is not None

        if values is None:
            values = [df[id].unique()[0] for id in identifiers]
        return ",".join([f"{id}={val}" for id, val in zip(identifiers, values)])

    # Set up labels
    if x_axis_label is None:
        x_axis_label = x_axis_col
    if y_axis_label is None:
        y_axis_label = y_axis_col
    if y_axis_col_secondary is not None and y_axis_label_secondary is None:
        y_axis_label_secondary = y_axis_col_secondary

    # Set up figure and axes
    fig, axes = None, []
    subplot_dfs = []

    if subplots_identifiers is not None:
        subplot_dfs = [y for _, y in df.groupby(subplots_identifiers, as_index=False)]
        subplot_count = len(subplot_dfs)

        # find "squarish" layout
        side1 = math.floor(math.sqrt(subplot_count))
        side2 = math.ceil(subplot_count / float(side1))

        # favor portrait layout
        subplot_rows = max(side1, side2)
        subplot_cols = min(side1, side2)

        # create subplots
        fig, axes = plt.subplots(nrows=subplot_rows, ncols=subplot_cols, figsize=(8,8))
    else:
        # make single axes by default
        subplot_dfs = [df]
        fig = plt.figure()
        axes = [fig.add_subplot(111)]
    
    # Get all unique group permutations.
    unique_groups = df.value_counts(group_identifiers).index.tolist()
    
    # Set up markers and colors
    markers = USABLE_MARKERS.copy()
    shuffle(markers)
    markers = cycle(markers)
    colors = cycle(cm.rainbow(np.linspace(0, 1, len(unique_groups))))

    # Set up y-axis legends only if necessary
    legend_handles = []
    if y_axis_col_secondary is not None:
        legend_handles.append(Line2D([0], [0], color='black', label=y_axis_label))
        legend_handles.append(Line2D([0], [0], color='black', linestyle='dotted', label=y_axis_label_secondary))
    
    # set colors and markers for all combinations of group identifiers used across all subplots.
    attr_map = {}
    for combi in unique_groups:
        # grab next available color and marker
        marker = next(markers)
        color = next(colors)

        # add to map
        attr_map[combi] = marker, color

        # add legend handle
        legend_line = Line2D(
            [0], [0], 
            color=color, marker=marker,
            label=get_identifiers_label(group_identifiers, list(combi))
        )
        legend_handles.append(legend_line)

    for df, ax_i in zip(subplot_dfs, np.ndindex(axes.shape)):
        ax = axes[ax_i]
        if subplots_identifiers is not None:
            ax.set_title(get_identifiers_label(subplots_identifiers, df=df))
        
        # Set labels for axes
        ax.set_xlabel(xlabel=x_axis_label)
        ax.set_ylabel(ylabel=y_axis_label)
        ax2 = None
        if y_axis_col_secondary is not None:
            ax2 = ax.twinx()
            ax2.set_ylabel(ylabel=y_axis_label_secondary)

        # Split DataFrame into distinct groups
        groups = [y for _, y in df.groupby(group_identifiers, as_index=False)]

        for grp in groups:
            marker, color = attr_map[tuple(grp[col].unique()[0] for col in group_identifiers)]
            grp.plot(x=x_axis_col, y=y_axis_col, kind='line', linestyle='solid', marker=marker, color=color, ax=ax)
            if y_axis_col_secondary is not None:
                grp.plot(x=x_axis_col, y=y_axis_col_secondary, kind='line', linestyle='dotted', marker=marker, color=color, ax=ax2)
        
        # remove all axes legends
        ax.get_legend().remove()
        if ax2 is not None:
            ax2.get_legend().remove()
        
    # set up legend
    fig.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1, 0.5))
    fig.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, bbox_inches='tight', dpi=1200)
    plt.close()