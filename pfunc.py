#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 14:59:42 2022.

Shared plot functions

@author: cdesbois
"""
from typing import Optional, Any

import matplotlib.pyplot as plt


def update_pltparams() -> None:
    """Update the matplotlib rcParams."""
    fontsize = "medium"  # large, medium
    params = {
        "font.sans-serif": ["Arial"],
        "font.size": 12,
        "legend.fontsize": fontsize,
        "figure.figsize": (12, 3.1),
        "axes.labelsize": fontsize,
        "axes.titlesize": fontsize,
        "xtick.labelsize": fontsize,
        "ytick.labelsize": fontsize,
        "axes.xmargin": 0,
    }
    plt.rcParams.update(params)
    plt.rcParams["axes.xmargin"] = 0  # no gap between axes and traces
    print("plot_func: updated the matplotlib rcParams (plot_func)")


def empty_data_fig(mes: str = "") -> plt.Figure:
    """
    Generate an empty figure message for empty/missing data.

    Parameters
    ----------
    mes : str, optional (default is None)
        the message to display.

    Returns
    -------
    fig : plt.Figure
        an empty figure.

    """
    fig = plt.figure()
    fig.text(
        0.5,
        0.5,
        mes,
        horizontalalignment="center",
        fontsize="x-large",
        verticalalignment="center",
    )
    return fig


def add_baseline(fig: plt.figure, param: Optional[dict[str, Any]] = None) -> None:
    """Annotate the base of the plot."""
    if param is None:
        param = {}
    fig.text(0.99, 0.01, "bgplot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param.get("file", ""), ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()


def color_axis(ax0: plt.Axes, spine: str = "bottom", color: str = "r") -> None:
    """
    Change the color of the label & tick & spine.

    Parameters
    ----------
    ax : plt.Axes
        the axis to work on.
    spine : str, optional (default is "bottom")
        optional location in ['bottom', 'left', 'top', 'right'] .
    color : str, optional (default is "r")
        the color to use.

    Returns
    -------
    None.
    """
    ax0.spines[spine].set_color(color)
    if spine == "bottom":
        ax0.xaxis.label.set_color(color)
        ax0.tick_params(axis="x", colors=color)
    elif spine in ["left", "right"]:
        ax0.yaxis.label.set_color(color)
        ax0.tick_params(axis="y", colors=color)
