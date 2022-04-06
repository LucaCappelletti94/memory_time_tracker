"""Submodule with plotting methods."""
from typing import List, Union
import os
from sanitize_ml_labels import sanitize_ml_labels
import matplotlib.patheffects as PathEffects
import humanize
import pandas as pd
import matplotlib.pyplot as plt
from .utils import has_completed_successfully, has_crashed_gracefully, has_crashed_ungracefully


def xformat_func(value, tick_number):
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
    return humanize.naturalsize(value * (1000**3))


def plot_reports(paths: Union[str, List[str]]):
    """Plot one or more reports from the provided path(s).

    Parameters
    ------------------------
    paths: Union[str, List[str]]
        Path(s) from where to load the reports
    """
    if isinstance(paths, str):
        paths = [paths]

    fig, axis = plt.subplots(figsize=(5, 5), dpi=200)
    axis.set_xlabel("Time")
    axis.set_ylabel("Memory")
    axis.xaxis.set_major_formatter(plt.FuncFormatter(xformat_func))
    axis.yaxis.set_major_formatter(plt.FuncFormatter(yformat_func))

    for path in paths:
        # Get the name of the report
        report_name = sanitize_ml_labels(
            ".".join(os.path.basename(path).split(".")[:-1])
        )
        # We load in a pandas DataFrame the tracked performance.
        df = pd.read_csv(
            path,
            engine="c"
        )
        # We drop the last line
        if has_completed_successfully(path):
            df = df[:-1]
        if has_crashed_gracefully(path):
            df = df[:-2]
        # Plot the current report line
        segments = axis.plot(*df.values.T, label=report_name)[0]
        # Show the skulls
        if has_crashed_gracefully(path) or has_crashed_ungracefully(path):
            x, y = df.iloc[-1].values
            txt = axis.text(
                x,
                y,
                "x",
                c=segments.get_color(),
                fontsize=12
            )
            txt.set_path_effects([
                PathEffects.withStroke(
                    linewidth=3,
                    foreground=segments.get_color(),
                ),
                PathEffects.withStroke(
                    linewidth=2,
                    foreground='w',
                    alpha=0.9
                )
            ])
    fig.legend()
