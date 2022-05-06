"""Submodule with plotting methods."""
from typing import List, Union
import os
from sanitize_ml_labels import sanitize_ml_labels
import matplotlib.patheffects as PathEffects
import humanize
import pandas as pd
import matplotlib.pyplot as plt
from .utils import has_completed_successfully, has_crashed_gracefully, has_crashed_ungracefully

TABLEAU = [
    "tab:blue",
    "tab:orange",
    "tab:green",
    "tab:red",
    "tab:purple",
    "tab:brown",
    "tab:pink",
    "tab:gray",
    "tab:olive",
    "tab:cyan",
]

def xformat_func(value, tick_number):
    """Return time value formatted in human readable."""
    if value == 0:
        return "0s"
    if value < 1e-9:
        return r"${:.2f}ps$".format(value * 1e12)
    if value < 1e-6:
        return r"${:.2f}ns$".format(value * 1e9)
    if value < 1e-3:
        return r"${:.2f}\mu s$".format(value * 1e6)
    if value < 1:
        return r"${:.2f}ms$".format(value * 1e3)
    if value < 60:
        return r"${:.2f}s$".format(value)
    if value < 3600:
        return r"${:.2f}m$".format(value / 60)

    return r"${:.2f}h$".format(value / 3600)


def yformat_func(value, tick_number):
    """Return memory value formatted in human readable."""
    return humanize.naturalsize(value * (1000**3))


def plot_reports(
    paths: Union[str, List[str]],
    use_log_scale_for_time: bool = True,
    use_log_scale_for_memory: bool = False,
    plot_single_report_lines: bool = True
):
    """Plot one or more reports from the provided path(s).

    Parameters
    ------------------------
    paths: Union[str, List[str]]
        Path(s) from where to load the reports
    use_log_scale_for_time: bool = True
        Whether to use log scale for the horizontal axis.
    use_log_scale_for_memory: bool = False
        Whether to use log scale for the vertical axis.
    plot_single_report_lines: bool = True
        Whether to plot the single report lines.
    """
    if isinstance(paths, str):
        paths = [paths]

    fig, axis = plt.subplots(figsize=(5, 5), dpi=200)
    axis.xaxis.set_major_formatter(plt.FuncFormatter(xformat_func))
    axis.yaxis.set_major_formatter(plt.FuncFormatter(yformat_func))

    # Handle scales and the relative axis labels.
    if use_log_scale_for_time:
        axis.set_xscale("log")
        axis.set_xlabel("Time (log scale)")
    else:
        axis.set_xlabel("Time")

    if use_log_scale_for_memory:
        axis.set_yscale("log")
        axis.set_xlabel("Memory (log scale)")
    else:
        axis.set_ylabel("Memory")

    # We group paths by base name so we can plot
    # the standard deviation as an area of the graph.
    grouped_paths = pd.DataFrame([
        {
            "path": path,
            "basename": os.path.basename(path)
        }
        for path in paths
    ]).groupby("basename")

    # We start to iterate on the groups
    for (basename, group), color in zip(grouped_paths, TABLEAU):
        report_name = sanitize_ml_labels(
            ".".join(basename.split(".")[:-1])
        )
        reports = []
        # We iterate over the report paths
        for path in group.path:
            # We load in a pandas DataFrame the tracked performance.
            report = pd.read_csv(path)

            # We drop the last line if it has completed successfully
            if has_completed_successfully(path):
                report = report[:-1]

            # And the last two lines if it has crashed gracefully
            if has_crashed_gracefully(path):
                report = report[:-2]

            # We add this report to the list of reports to compute
            # the standard deviation and mean.
            reports.append(report)

            if not plot_single_report_lines:
                continue

            # Plot the current report line
            axis.plot(*report.values.T, color=color)

            # Show the skulls
            if has_crashed_gracefully(path) or has_crashed_ungracefully(path):
                x, y = report.iloc[-1].values
                txt = axis.text(
                    x,
                    y,
                    "x",
                    c=color,
                    fontsize=12
                )
                txt.set_path_effects([
                    PathEffects.withStroke(
                        linewidth=3,
                        foreground=color,
                    ),
                    PathEffects.withStroke(
                        linewidth=2,
                        foreground='w',
                        alpha=0.9
                    )
                ])
        
        reports = pd.concat(reports)
        mean_time, mean_memory = reports.groupby(reports.index).mean().values.T
        _, std_memory = reports.groupby(reports.index).std().values.T

        axis.fill_between(
            mean_time,
            mean_memory-std_memory,
            mean_memory+std_memory,
            color=color,
            alpha=0.1
        )
        axis.plot(
            mean_time,
            mean_memory-std_memory,
            color=color,
            linewidth=0.5,
            alpha=0.1
        )
        axis.plot(
            mean_time,
            mean_memory+std_memory,
            color=color,
            linewidth=0.5,
            alpha=0.1
        )

        axis.plot(
            mean_time,
            mean_memory,
            linewidth=2,
            color=color,
            label=report_name,
        )

    fig.legend(
        prop={'size': 8}
    )
