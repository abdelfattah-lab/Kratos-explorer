import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

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


def plot_result(axis1, axis2, datapoints, description1='', description2='', description3='', title='', save_name='', elevation=25, azimuth=-145, alpha=1.0):
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