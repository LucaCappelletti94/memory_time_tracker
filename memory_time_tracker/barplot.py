"""Submodule with plotting methods."""
from typing import List, Union, Tuple, Dict
import os
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from barplots import barplots
import pandas as pd
from .utils import has_completed_successfully, has_crashed_gracefully


def load_report(path: str) -> pd.DataFrame:
    # We load in a pandas DataFrame the tracked performance.
    report = pd.read_csv(path)

    # We drop the last line if it has completed successfully
    if has_completed_successfully(path):
        report = report[:-1]

    # And the last two lines if it has crashed gracefully
    if has_crashed_gracefully(path):
        report = report[:-2]

    return report


def plot_report_barplots(
    paths: Union[str, List[str]],
    **kwargs: Dict
) -> Tuple[List[Figure], List[Axes]]:
    """Plot one or more reports from the provided path(s).

    Parameters
    ------------------------
    paths: Union[str, List[str]]
        Path(s) from where to load the reports.
        File with the same basename will be averaged out.
    **kwargs: Dict
        Parameters to forward to plots.
    """
    if isinstance(paths, str):
        paths = [paths]

    # We start to iterate on the groups
    df = pd.DataFrame([
        {
            "basename": basename,
            "memory": report.ram.max(),
            "time": report.delta.max(),
        }
        for report, basename in (
            (
                load_report(path),
                ".".join(os.path.basename(path).split(".")[:-1])
            )
            for path in paths
        )
    ])

    return barplots(
        df,
        groupby=["basename"],
        use_multiprocessing=False,
        **kwargs
    )
