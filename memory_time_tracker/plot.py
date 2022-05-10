"""Submodule with plotting methods."""
from typing import List, Union
import os
from sanitize_ml_labels import sanitize_ml_labels
import matplotlib.patheffects as PathEffects
import humanize
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from scipy.signal import savgol_filter
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


def remove_duplicated_legend_labels(
    axes: Axes,
    legend_position: str,
):
    """Remove duplicated labels from the plot legend.

    Parameters
    ---------------
    axes: Axes
        Axes where to show the labels.
    legend_position: str
        Legend position.
    """
    handles, labels = axes.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    axes.legend(
        by_label.values(),
        sanitize_ml_labels(by_label.keys()),
        loc=legend_position,
        prop={'size': 8}
    )


def xformat_func(value, tick_number):
    """Return time value formatted in human readable."""
    if value == 0:
        formatted_time = "0"
        unit = "s"
    elif value < 1e-9:
        formatted_time = "{:.1f}".format(value * 1e12)
        unit = "ps"
    elif value < 1e-6:
        formatted_time = "{:.1f}".format(value * 1e9)
        unit = "ns"
    elif value < 1e-3:
        formatted_time = "{:.1f}".format(value * 1e6)
        unit = "\mu s"
    elif value < 1:
        formatted_time = "{:.1f}".format(value * 1e3)
        unit = "ms"
    elif value < 60:
        formatted_time = "{:.1f}".format(value)
        unit = "s"
    elif value < 3600:
        formatted_time = "{:.1f}".format(value / 60)
        unit = "m"
    else:
        formatted_time = "{:.1f}".format(value / 3600)
        unit = "h"

    formatted_time = formatted_time.replace(".0", "")

    return r"${formatted_time}{unit}$".format(
        formatted_time=formatted_time,
        unit=unit
    )


def yformat_func(value, tick_number):
    """Return memory value formatted in human readable."""
    return humanize.naturalsize(value * (1000**3))


def filter_signal(
    y: List[float],
    window: int = 17,
    polyorder: int = 3
) -> List[float]:
    """Return filtered signal using savgol filter.

    Parameters
    ----------------------------------
    y: List[float]
        The vector to filter.
    window: int = 17
        The size of the window.
        This value MUST be an odd number.
    polyorder: int = 3
        Order of the polynomial.

    Returns
    ----------------------------------
    Filtered vector.
    """
    # The window cannot be smaller than 7 and cannot be greater
    # than the length of the given vector.
    window = max(7, min(window, len(y)))
    # If the window is not odd we force it to be so.
    if window % 2 == 0:
        window -= 1
    # If the window is still bigger than the size of the given vector
    # we return the vector unfiltered.
    if len(y) < window:
        return y
    # Otherwise we apply the savgol filter.
    return savgol_filter(y, window, polyorder)


def _plot_reports(
    figure: Figure,
    axis: Axes,
    paths: Union[str, List[str]],
    reduce: str = "max",
    use_log_scale_for_time: bool = True,
    use_log_scale_for_memory: bool = False,
    plot_single_report_lines: bool = True,
    show_memory_std: bool = False,
    apply_savgol_filter: bool = True,
    savgol_filter_window_size: int = 33,
    aggregated_line_line_width: Union[int, str] = "auto"
):
    """Plot one or more reports from the provided path(s).

    Parameters
    ------------------------
    figure: Figure
        The figure to plot on.
    axis: Axes
        The axis to plot on.
    paths: Union[str, List[str]]
        Path(s) from where to load the reports.
        File with the same basename will be averaged out.
    reduce: str = "max"
        How to reduce the values between the different executions.
    use_log_scale_for_time: bool = True
        Whether to use log scale for the horizontal axis.
    use_log_scale_for_memory: bool = False
        Whether to use log scale for the vertical axis.
    plot_single_report_lines: bool = True
        Whether to plot the single report lines.
    show_memory_std: bool = False
        Whether to show standard deviation.
    apply_savgol_filter: bool = True
        On long running benchmarks, expecially when using
        multiple holdouts, there may be a significant amount
        of noise. In these cases, a savgol filter may
        increase significantly how understandable the plot will be.
    savgol_filter_window_size: int = 33
        Size of the window to use for the savgol filter.
    aggregated_line_line_width: Union[int, str] = "auto"
        The linewidth to use to plot the aggregated line.
        By default, with the value "auto", with set it to 1
        when the single reports should not be shown and 2 otherwise.
    """
    if isinstance(paths, str):
        paths = [paths]

    if reduce != "max":
        raise ValueError(
            "So far we only support the reduction using max. "
            "Would you like another reduce? Open an issue or a pull request "
            "on the memory time tracker repository."
        )

    if aggregated_line_line_width == "auto":
        if plot_single_report_lines:
            aggregated_line_line_width = 2
        else:
            aggregated_line_line_width = 1

    # Handle scales and the relative axis labels.
    if use_log_scale_for_time:
        axis.set_xscale("log")
        axis.set_xlabel("Time (log scale)")
        # Set the minor tick interval in log scale
        axis.xaxis.set_minor_locator(
            LogLocator(base=10.0, subs=[0.2, 0.4, 0.6, 0.8], numticks=100)
        )
        # Do not format minor ticks
        axis.xaxis.set_minor_formatter(
            NullFormatter()
        )
    else:
        axis.set_xlabel("Time")

    if use_log_scale_for_memory:
        axis.set_yscale("log")
        axis.set_ylabel("Memory (log scale)")
    else:
        axis.set_ylabel("Memory")

    axis.xaxis.set_major_formatter(plt.FuncFormatter(xformat_func))
    axis.yaxis.set_major_formatter(plt.FuncFormatter(yformat_func))
    axis.grid(True, which="both", ls="-", alpha=0.3)

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

        if reduce == "max":
            aggregated_report = reports.groupby(reports.index).max()

        aggregated_report.sort_values("delta", inplace=True)
        aggregated_time, aggregated_memory = aggregated_report.values.T

        if apply_savgol_filter:
            aggregated_memory = filter_signal(
                aggregated_memory,
                window=savgol_filter_window_size
            )

        if show_memory_std:
            _, std_memory = reports.groupby(
                reports.index
            ).std().loc[aggregated_report.index].to_numpy().T

            if apply_savgol_filter:
                std_memory = filter_signal(
                    std_memory,
                    window=savgol_filter_window_size
                )

            axis.fill_between(
                aggregated_time,
                aggregated_memory-std_memory,
                aggregated_memory+std_memory,
                color=color,
                alpha=0.1
            )
            axis.plot(
                aggregated_time,
                aggregated_memory-std_memory,
                color=color,
                linewidth=0.5,
                alpha=0.1
            )
            axis.plot(
                aggregated_time,
                aggregated_memory+std_memory,
                color=color,
                linewidth=0.5,
                alpha=0.1
            )

        axis.plot(
            aggregated_time,
            aggregated_memory,
            linewidth=aggregated_line_line_width,
            color=color,
            label=report_name,
        )


def plot_reports(
    paths: Union[str, List[str]],
    reduce: str = "max",
    use_log_scale_for_time: bool = True,
    use_log_scale_for_memory: bool = False,
    plot_single_report_lines: bool = True,
    show_memory_std: bool = False,
    apply_savgol_filter: bool = True,
    savgol_filter_window_size: int = 33,
    aggregated_line_line_width: Union[int, str] = "auto",
    show_linear_and_log_scale: bool = True
):
    """Plot one or more reports from the provided path(s).

    Parameters
    ------------------------
    paths: Union[str, List[str]]
        Path(s) from where to load the reports.
        File with the same basename will be averaged out.
    reduce: str = "max"
        How to reduce the values between the different executions.
    use_log_scale_for_time: bool = True
        Whether to use log scale for the horizontal axis.
    use_log_scale_for_memory: bool = False
        Whether to use log scale for the vertical axis.
    plot_single_report_lines: bool = True
        Whether to plot the single report lines.
    show_memory_std: bool = False
        Whether to show standard deviation.
    apply_savgol_filter: bool = True
        On long running benchmarks, expecially when using
        multiple holdouts, there may be a significant amount
        of noise. In these cases, a savgol filter may
        increase significantly how understandable the plot will be.
    savgol_filter_window_size: int = 33
        Size of the window to use for the savgol filter.
    aggregated_line_line_width: Union[int, str] = "auto"
        The linewidth to use to plot the aggregated line.
        By default, with the value "auto", with set it to 1
        when the single reports should not be shown and 2 otherwise.
    show_linear_and_log_scale: bool = True
        Whether to make one plot with the parameters or two
        using both a linear and logaritmic scal
        for the horizontal (the time) axis
    """

    if show_linear_and_log_scale:
        figure, (linear_axis, log_axis) = plt.subplots(
            ncols=2,
            figsize=(10, 5),
            dpi=200
        )
        for axis, scale in (
            (linear_axis, False),
            (log_axis, True),
        ):
            _plot_reports(
                figure,
                axis=axis,
                paths=paths,
                reduce=reduce,
                use_log_scale_for_time=scale,
                use_log_scale_for_memory=use_log_scale_for_memory,
                plot_single_report_lines=plot_single_report_lines,
                show_memory_std=show_memory_std,
                apply_savgol_filter=apply_savgol_filter,
                savgol_filter_window_size=savgol_filter_window_size,
                aggregated_line_line_width=aggregated_line_line_width,
            )

            remove_duplicated_legend_labels(
                axis,
                "best",
            )
    else:
        figure, axis = plt.subplots(figsize=(1, 5), dpi=200)
        _plot_reports(
            figure,
            axis=axis,
            paths=paths,
            reduce=reduce,
            use_log_scale_for_time=use_log_scale_for_time,
            use_log_scale_for_memory=use_log_scale_for_memory,
            plot_single_report_lines=plot_single_report_lines,
            show_memory_std=show_memory_std,
            apply_savgol_filter=apply_savgol_filter,
            savgol_filter_window_size=savgol_filter_window_size,
            aggregated_line_line_width=aggregated_line_line_width,
        )

        remove_duplicated_legend_labels(
            axis,
            "best",
        )

    figure.tight_layout()
