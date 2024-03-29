#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 15:26:14 2016.

@author: cdesbois
"""

import os
import logging
from typing import Any, Set, Optional, Callable
from math import floor, ceil

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.figure import Figure
from matplotlib import rcParams
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import pandas as pd

logfile = os.path.expanduser(os.path.join("~", "blood_gases.log"))
logging.basicConfig(
    level=logging.INFO,
    force=True,
    format="%(levelname)s:%(funcName)s:%(message)s",
    filename=logfile,
    filemode="w+",
    # handlers=[logging.FileHandler(logfile)],
)

rcParams.update({"font.size": 18, "font.family": "serif"})


def round_lims(limits: Set, round_value: float = 5) -> tuple[float, float]:
    """
    Return a tuple (min, max) of floor-ceil % round_value.

    Parameters
    ----------
    limits: Set
        contain the axes limits (real and expected).
    round_value : float, optional(efault is 5)
        the rounded value desired

    Returns
    -------
    Tuple
        (min, max) to be used

    """
    mini = floor(min(limits) / round_value) * round_value
    maxi = ceil(max(limits) / round_value) * round_value
    return (mini, maxi)


# ==============================================================================
class Gas:
    """
    Gas class to manipulate bloodGases.

    + Gas(spec='horse', hb=12, fio2=0.21, po2=95, ph=7.4, pco2=40, hco3=24, etco2=38)

    + attributes :
        spec : 'horse' or 'dog'\
        hb :    hemoblobine concentration \
        fio2 : inspiration fraction of oxygen (0 to 1) \
        po2 :    partial pressure of oxyene (mmHg) \
        ph :    pH \
        pco2 : partial pressure of CO2 (mmHg) \
        hco3 : HCO3 concentration in the blood \
        etco2 : end Tidale CO2 (mmHg) \
    + methods :
        __str__: return the attributes \
        casc : return the O2 cascade (AlvelarGasEquation) \
        piecasc : return the values to build the cas for all gases \

    """

    # to store the gasesObj
    gasesGasList: list[Any] = []

    def __init__(self, **kwargs: Any) -> None:
        self.spec = kwargs.get("spec", "horse")
        self.hb = kwargs.get("hb", 12)
        self.fio2 = kwargs.get("fio2", 0.21)
        if self.fio2 >= 1:
            self.fio2 = round(self.fio2 / 100, 2)
        self.po2 = kwargs.get("po2", 95)
        self.ph = kwargs.get("ph", 7.4)
        self.pco2 = kwargs.get("pco2", 40)
        self.hco3 = kwargs.get("hco3", 24)
        self.etco2 = kwargs.get("etco2", 38)
        Gas.gasesGasList.append(self)

    @classmethod
    def return_gasList(cls) -> list[Any]:
        """Get global list of gas objects."""
        return Gas.gasesGasList

    def values(self) -> dict[str, Any]:
        """Return a dico of measured values."""
        values = {
            "spec": self.spec,
            "hb": self.hb,
            "fio2": self.fio2,
            "po2": self.po2,
            "ph": self.ph,
            "pco2": self.pco2,
            "hco3": self.hco3,
        }
        return values

    # to be able to print values
    def __str__(self) -> str:
        """Str description."""
        txt1 = f"species={self.spec} hb={self.hb} fio2={self.fio2} po2=self.po2)"
        txt2 = f"ph={self.ph} pco2={self.pco2} hco3={self.hco3} etco2={self.etco2}"
        return f"{txt1} \n {txt2}"

    def casc(self) -> list[float]:
        """
        Compute the O2 cascade.

        Returns
        -------
        list[float]
            list (pinsp, paerien, pAo2 and paO2)
        """
        ph2o = 47
        patm = 760
        casc = []
        # casc = ([pinsp, paerien, pAo2, pao2])
        casc.append(self.fio2 * patm)
        casc.append(self.fio2 * (patm - ph2o))
        casc.append(self.fio2 * (patm - ph2o) - self.pco2 / 0.8)
        casc.append(self.po2)
        return casc

    def piecasc(self) -> list[dict[str, float]]:
        """
        Compute the O2 cascade values in %.

        return oxygen cascade values (%),
        input params = fio2 (0.), paco2 (mmHg) pao2 (mmHg)
        output = casc (list) ie [pinsp, paerien, pAO2, paO2]


        Returns
        -------
        list[dict[str, float]]
            keys: inspired, aerial & alveolar
            values : [pinsp, paerial, pAo2 and paO2]

        """
        ph2o = 47
        patm = 760
        inspired = {}
        inspired["O2"] = self.fio2 * patm
        inspired["N2"] = patm - inspired["O2"]

        aerial = {}
        aerial["O2"] = self.fio2 * (patm - ph2o)
        aerial["H2O"] = ph2o
        aerial["N2"] = patm - aerial["O2"] - aerial["H2O"]

        alveolar = {}
        alveolar["O2"] = self.fio2 * (patm - ph2o) - self.pco2 / 0.8
        alveolar["H2O"] = ph2o
        alveolar["CO2"] = self.pco2
        alveolar["N2"] = patm - alveolar["O2"] - ph2o - self.pco2

        pieCas = [inspired, aerial, alveolar]
        return pieCas


# ==============================================================================
# hill function parameters
def satFit(species: str) -> dict[str, Any]:
    """
    Return hill function parameters to be able to rebuild saturation curve.

    Parameters
    ----------
    species : str
        species in ["horse", "dog", "cat", "human"]

    Returns
    -------
    Dict[str, Any]
        keys : 'base', 'max', 'rate', 'xhalf'

    """
    species_list = ["horse", "dog", "cat", "human"]
    if species not in species_list:
        print(f"species should be in {species_list}")
        logging.warning(f"{species=}, replaced by 'horse")
        species = "horse"
    sat_curv: dict[str, list[Any]] = {}
    sat_curv["id"] = species_list
    # sat_curv['horse'] = ([2, 99.427, 2.7, 23.8])
    sat_curv["base"] = [2, 6.9, 0, 0]
    sat_curv["max"] = [99.427, 100, 100, 100]
    sat_curv["rate"] = [2.7, 2.8, 2, 2.8]
    sat_curv["xhalf"] = [23.8, 33.3, 0, 0]

    hillparams_df = pd.DataFrame(sat_curv).set_index("id").T
    hillparams = hillparams_df[species].to_dict()

    return hillparams


# TODO check with previous values

# fit Hill fonction:
# r$ fit = base + \frac{max-base}{(1 + (\frac{xhalf}{x})^{rate})} $
# r$ SatHb_{02} = base + \frac{max-base}{(1 + (\frac{P_{50}}{P_{O_2}})^{n})} $ (n= coeff de Hill)
# base 	=2.0095 ± 0.345
# max 	=99.427 ± 0.327
# rate 	=2.7
# xhalf	=23.8

# 	dog:
#     base 	=6.9262 ± 0.137
#    	max 	=100.16 ± 0.0224
#    	rate 	=2.8702 ± 0.00521
#    	xhalf	=33.263 ± 0.037

# --------------------------------------
def satHbO2(
    species: str, po2: float
) -> float:  # species = horse or dog or cat or human
    """
    Return the satHbO2 value.

    Parameters
    ----------
    species : str
        in [horse, dog, cat, human]
    po2: float
        the arterial oxygen value
    Returns
    -------
    float:
        the sat value
    """
    #    species = mes['species']
    #    po2 = mes['po2']
    hill_params = satFit(species)
    sat = hill_params["base"] + (hill_params["max"] - hill_params["base"]) / (
        1 + ((hill_params["xhalf"] / po2) ** hill_params["rate"])
    )
    # if (sat > 100):
    #  sat = 100
    return sat


def caO2(species: str, hb: float, po2: float) -> float:
    """
    Return the the arterial content in oxygen (caO2).

    Parameters
    ----------
    species : str
        in [horse, dog, cat, human].
    hb : float
        the Hb content.
    po2 : float
        the arterial oxygen (in mmHg).

    Returns
    -------
    float
        the arterial content in oxygen.

    """
    #  po2 = mes['po2']
    #  hb = mes ['hb']
    sat = satHbO2(species, po2)
    cao2 = 1.38 * sat * hb + 0.003 * po2
    return cao2


# %
def plot_acidbas(
    gases: list,
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot the acid-base analysis.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    savedir : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
        the plot
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    gas = gases[num]
    species = gas.spec
    if species == "horse":
        phRange = [7.35, 7.45]
    else:
        phRange = [7.35, 7.42]
    ph = gas.ph
    pco2 = gas.pco2
    hco3 = gas.hco3

    if pyplot:
        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(14, 8), frameon=True)
    else:
        fig = Figure(figsize=(14, 8), frameon=True)
        axes = []
        for i in range(1, 4):
            axes.append(fig.add_subplot(3, 1, i))
    # fig.suptitle("acidobasique ($pH, \ Pa_{CO_2}, \ HCO_3^-$ )", fontsize=24,
    #              color='tab:gray')
    legs = [(r"$pH$", "k"), (r"$P_{CO_2}$", "tab:blue"), (r"$HCO_3^-$", "tab:orange")]
    for ax, leg in zip(axes, legs):
        ax.axhline(0, color="tab:gray")
        ax.text(
            0.05,
            0.5,
            leg[0],
            fontsize=22,
            color=leg[1],
            horizontalalignment="left",
            verticalalignment="center",
            transform=ax.transAxes,
            backgroundcolor="w",
        )
    txt = f"acid {'-' * 76} alcalin"
    fig.suptitle(txt, color="tab:gray")
    ax = axes[0]
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax.plot(
        phRange,
        [0, 0],
        label="line 1",
        linewidth=5,
        color="tab:gray",
        marker="d",
        markersize=10,
    )
    ax.plot([ph], [0], "v-", color="tab:red", markersize=32, markeredgecolor="k")
    phmin, phmax = 7.3, 7.5
    if ph >= 7.5:
        phmax = ph + 0.1
    if ph <= 7.3:
        phmin = ph - 0.1
    ax.set_xlim([phmin, phmax])

    ax = axes[1]
    co2min, co2max = 25, 55
    if pco2 >= co2max:
        co2max = pco2 + 5
    if pco2 <= co2min:
        co2min = pco2 - 5
    ax.plot(
        [35, 45],
        [0, 0],
        label="line 1",
        linewidth=5,
        color="tab:blue",
        alpha=0.8,
        marker="d",
        markersize=10,
    )
    ax.plot([pco2], [0], "v-", color="tab:red", markersize=32, markeredgecolor="k")
    ax.set_xlim([co2max, co2min])

    ax = axes[2]
    hco3min, hco3max = 15, 35
    if hco3 >= hco3max:
        hco3max = hco3 + 5
    if hco3 <= hco3min:
        hco3min = hco3 - 5
    ax.plot(
        [20, 30],
        [0, 0],
        label="line 1",
        linewidth=5,
        color="tab:orange",
        marker="d",
        markersize=10,
    )
    ax.plot([hco3], [0], "v-", color="tab:red", markersize=32, markeredgecolor="k")
    ax.set_xlim([hco3min, hco3max])
    for ax in axes:
        ax.get_yaxis().set_visible(False)
        ax.tick_params(colors="tab:grey")
        for spine in ["left", "top", "right", "bottom"]:
            ax.spines[spine].set_visible(False)
    if pyplot:
        if saveit:
            name = os.path.join(savedir, (str(ident) + "acidBase"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
        plt.show()
    fig.text(0.99, 0.01, "plot_acidbas", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# ------------------------------------
def plot_display(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot a display of the gas values.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    savedir : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
        the plot
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    # title = "mesured values"
    rows = ["num", "spec", "hb", "fio2", "po2", "ph", "pco2", "hco3", "etco2"]
    usualVal: dict[str, Any] = {}
    usualVal["num"] = num
    usualVal["spec"] = gases[num].spec
    usualVal["hb"] = 12
    usualVal["fio2"] = "0.21 - 1"
    usualVal["po2"] = "3-5 * fio2"
    usualVal["ph"] = "7.35 - 7.45"
    usualVal["pco2"] = "40, (35-45)"
    usualVal["hco3"] = "24 (20-30)"
    usualVal["etco2"] = "38 (35-45)"

    cols = ["mesure", "usual"]
    data = []
    # NB 'num' is not a gas attibute
    data.append([num, num])
    for row in rows[1:]:
        data.append([getattr(gases[num], row), usualVal[row]])

    fig = plt.figure(figsize=(14, 5)) if pyplot else Figure(figsize=(14, 5))
    if pyplot:
        fig = plt.figure(figsize=(14, 5))
    else:
        fig = Figure(figsize=(14, 5))
    # fig. suptitle(title)
    ax = fig.add_subplot(111)
    ax.axis("off")
    table = ax.table(
        cellText=data,
        rowLabels=rows,
        colLabels=cols,
        loc="upper center",
        cellLoc="center",
        colWidths=[0.2, 0.25],
        rowLoc="center",
        edges="R",
    )
    table.auto_set_font_size(False)
    table.scale(1, 2.5)

    if pyplot:
        # fig.set.tight_layout(True)
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "display"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(0.99, 0.01, "plot_display", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# %------------------------------------
def phline(val: float) -> list[str]:
    """
    Return a list containing the morpion display for pH.

    Parameters
    ----------
    val : float
        the pH value.

    Returns
    -------
    list[str]
        the signs to use for the morpion display.

    """
    ref = [7.2, 7.35, 7.45, 7.5]
    # base
    arrows = ["-", "-", "-"]
    # low´´
    if val < ref[1]:
        arrows[0] = "x"
    if val < ref[0]:
        arrows[0] = "<<"
    # middle
    if ref[1] <= val <= ref[2]:
        arrows[1] = "x"
    # hight
    if ref[2] < val:
        arrows[2] = "x"
    if ref[3] < val:
        arrows[2] = ">>"
    return arrows


def co2line(val: float) -> list[str]:
    """
    Return a list containing the morpion display for CO2.

    Parameters
    ----------
    val : float
        the co2 value (in mmHg).

    Returns
    -------
    list[str]
        the signs to use for the morpion display.

    """
    ref = [60, 42, 38, 30]  # NB data are presented in acid , norm, basic order
    arrows = ["-", "–", "-"]
    if val > ref[1]:
        arrows[0] = "x"
    if val > ref[0]:
        arrows[0] = "<<"
    if ref[1] >= val >= ref[2]:
        arrows[1] = "x"
    if ref[2] > val:
        arrows[2] = "x"
    if ref[3] > val:
        arrows[2] = ">>"
    return arrows


def hco3line(val: float) -> list[str]:
    """
    Return a list containing the morpion display for hco3-.

    Parameters
    ----------
    val : float
        the hco3- value.

    Returns
    -------
    list[str]
        the signs to use for the morpion display.

    """
    ref = [14, 22, 26, 32]
    arrows = ["-", "–", "-"]
    if val < ref[1]:
        arrows[0] = "x"
    if val < ref[0]:
        arrows[0] = "<<"
    if ref[1] <= val <= ref[2]:
        arrows[1] = "x"
    if ref[2] < val:
        arrows[2] = "x"
    if ref[3] < val:
        arrows[2] = ">>"
    return arrows


def plot_morpion(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot a 'morpion like' display.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
        the plot
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    gas = gases[num]
    title = (
        "pH=" + str(gas.ph) + r"    pco2=" + str(gas.pco2) + "    hco3=" + str(gas.hco3)
    )
    data = []
    data.append(phline(gas.ph))
    data.append(co2line(gas.pco2))
    data.append(hco3line(gas.hco3))

    cols = ("acide", "norm", "alcalin")
    rows = (r"$pH$", r"$P_{CO_2}$", r"$HCO_3^-$")
    if pyplot:
        fig = plt.figure(figsize=(14, 5))
    else:
        fig = Figure(figsize=(14, 5))
    fig.suptitle(title, color="tab:gray")
    # plt.title(title)
    ax = fig.add_subplot(111)
    ax.axis("off")
    # build the table
    table = ax.table(
        cellText=data,
        rowLabels=rows,
        colLabels=cols,
        loc="upper center",
        cellLoc="center",
        rowLoc="center",
        colWidths=[0.15, 0.15, 0.15],
    )
    table.auto_set_font_size(False)
    table.scale(1, 5)
    #    #fig.set.tight_layout(True)
    # fig.set_tight_layout(True)
    if pyplot:
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "morpion"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)

    fig.text(0.99, 0.01, "plot_morpion", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# %
def plot_o2(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot O2.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
        the plot
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    gas = gases[num]
    po2 = gas.po2
    fig = plt.figure(figsize=(14, 3)) if pyplot else Figure(figsize=(14, 3))
    # if pyplot:
    #     fig = plt.figure(figsize=(14, 3))
    # else:
    #     fig = Figure(figsize=(14, 3))
    # fig.suptitle("oxygénation : $Pa_{O_2}$ ", fontsize=24, backgroundcolor='w',
    #              color='tab:gray')
    ax = fig.add_subplot(111)
    ax.axhline(0, color="tab:gray")
    ax.plot(
        [90, 100],
        [0, 0],
        label="line 1",
        linewidth=5,
        color="tab:green",
        marker="d",
        markersize=10,
    )
    ax.plot([po2], [0], "v-", color="tab:red", markersize=32, markeredgecolor="k")
    if po2 < 120:
        ax.set_xlim([po2 - 20, 120])
    else:
        ax.set_xlim([70, po2 + 20])
    ax.text(
        0.05,
        0.5,
        r"$P_{O_2}$",
        fontsize=32,
        color="tab:green",
        horizontalalignment="left",
        verticalalignment="center",
        transform=ax.transAxes,
        backgroundcolor="w",
    )
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(True)
    # ax.grid()
    ax.axes.tick_params(colors="tab:gray")
    # fig.set.tight_layout(True)
    if pyplot:
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "O2"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)

    fig.text(0.99, 0.01, "plot_o2", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# ------------------------------------
def plot_ventil(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot ventil.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    gas = gases[num]
    po2 = gas.po2
    pco2 = gas.pco2

    if pyplot:
        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(14, 6))
        # fig = plt.figure(figsize=(14, 6))
    else:
        fig = Figure(figsize=(14, 8), frameon=True)
        axes = []
        for i in range(1, 3):
            axes.append(fig.add_subplot(3, 1, i))
    fig.suptitle("ventilation", color="tab:gray")

    for ax in axes:
        ax.axhline(0, color="tab:gray")

    ax = axes[0]
    ax.plot(
        [90, 100],
        [0, 0],
        label="line 1",
        linewidth=3,
        marker="d",
        markersize=10,
        color="tab:green",
    )
    ax.plot(
        [po2], [0], "v-", color="tab:red", markersize=32, markeredgecolor="k"
    )  # po2
    if po2 < 120:
        ax.set_xlim([po2 - 20, 120])
    else:
        ax.set_xlim([70, po2 + 20])
    ax.text(
        0.05,
        0.5,
        r"$P_{O_2}$",
        fontsize=32,
        color="tab:green",
        horizontalalignment="left",
        verticalalignment="center",
        transform=ax.transAxes,
        backgroundcolor="w",
    )

    ax = axes[1]
    ax.plot([35, 45], [0, 0], label="line 1", linewidth=3, marker="d", markersize=10)
    ax.plot(
        [pco2], [0], "v-", color="tab:red", markersize=32, markeredgecolor="k"
    )  # pco2
    co2min, co2max = 25, 55
    if pco2 >= co2max:
        co2max = pco2 + 5
    if pco2 <= co2min:
        co2min = pco2 - 5
    ax.set_xlim([co2min, co2max])
    ax.text(
        0.05,
        0.5,
        r"$P_{CO_2}$",
        fontsize=32,
        color="tab:blue",
        horizontalalignment="left",
        verticalalignment="center",
        transform=ax.transAxes,
        backgroundcolor="w",
    )

    for ax in axes:
        ax.axes.tick_params(colors="tab:gray")
        # ax.grid()
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(True)
        for spine in ["left", "top", "right", "bottom"]:
            ax.spines[spine].set_visible(False)
    # #fig.set.tight_layout(True)
    if pyplot:
        if saveit:
            name = os.path.join(savedir, (str(ident) + "ventil"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
        plt.show()
    fig.text(0.99, 0.01, "plot_ventil", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# ------------------------------------
def plot_pieCasc(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pcent: bool = True,
    pyplot: bool = True,
) -> plt.Figure:
    # fio2=0.21, paco2=40
    """
    Pie charts or gas % content.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    titles = ["inspiré", "aérien", "alvéolaire"]
    explodes = [[0.1, 0], [0, 0, 0.3], [0, 0, 0, 0.3]]

    labels = ["$N_2$", "$O_2$", "$H_2O$", "$CO_2$"]
    colors = ["tab:gray", "tab:green", "tab:cyan", "tab:orange"]
    valKeys = ["N2", "O2", "H2O", "CO2"]
    try:
        gas = gases[num]
    except IndexError:
        logging.warning(f"{num=} not in gases lenght")
        gas = gases[0]
    val = gas.piecasc()
    for d in val:
        if any(np.isnan(x) for x in d.values()):
            print("plot_pieCas, some values are Nan : aborted")
            return plt.figure()

    if pyplot:
        fig = plt.figure(figsize=(14, 6))  # (figsize=(14, 3))
    else:
        fig = Figure(figsize=(15, 6))  # (figsize=(14, 3))

    # fig.suptitle("inspiré,    aérien,    alvéolaire ", fontsize=24)
    for i in range(1, 4):  # 1, 2, 3
        ax = fig.add_subplot(1, 3, i)
        ax.set_title(titles[i - 1], y=0.99, alpha=0.5)
        values = []
        for ind in valKeys[: i + 1]:
            values.append(val[i - 1][ind])
        if pcent:
            ax.pie(
                values,
                explode=explodes[i - 1],
                labels=labels[: i + 1],
                colors=colors[: i + 1],
                autopct="%1.1f",
                counterclock=False,
                textprops={"alpha": 0.6},
                wedgeprops={"alpha": 0.7, "linewidth": 1, "ec": "w"},
            )
            # use autopct='%1.1f%%' to display the % symbol
            fig.text(0.5, 0.9, "en %", alpha=0.5, horizontalalignment="center")
        else:
            ax.pie(
                values,
                explode=explodes[i - 1],
                labels=labels[: i + 1],
                colors=colors[: i + 1],
                autopct=lambda p: "{:.0f}".format(p * 760 / 100),
                counterclock=False,
                textprops={"alpha": 0.6},
                wedgeprops={"alpha": 0.7, "linewidth": 1, "ec": "w"},
            )
            fig.text(0.5, 0.9, "en mmHg", alpha=0.5, horizontalalignment="center")

    # plt.text(0.5, 0.1, r'$$P_AO_2 = FiO_2 (P_{atm} - P_{H_2O}) - Pa_{CO_2}$$', horizontalalignment='center',
    # verticalalignment='center')#, transform = ax2.transAxes)
    # fig.set.tight_layout(True)
    # alpha
    if pyplot:
        fig.tight_layout()
        if saveit:
            if pcent:
                name = os.path.join(savedir, (str(ident) + "pieCascPercent"))
            else:
                name = os.path.join(savedir, (str(ident) + "pieCasc"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(0.99, 0.01, "plot_pieCasc", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# ----------------------------------------------
def plot_cascO2(
    gases: list[Any],
    nums: list,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot the O2 cascade.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    nums : list[int]
        location(s) in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
        histogram
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    # if just an integer was passed to the function
    if type(nums) != list:
        nums = [
            nums,
        ]
    if nums[0] != 0:
        nums.insert(0, 0)
    cascades = {}
    for num in nums:
        if num in range(len(gases)):
            gas = gases[num]
            cascades[num] = gas.casc()
    fig = plt.figure(figsize=(14, 6)) if pyplot else Figure(figsize=(16, 8))
    # if pyplot:
    #     fig = plt.figure(figsize=(14, 6))
    # else:
    #     fig = Figure(figsize=(16, 8))

    fig.suptitle(
        r"$Palv_{0_2} = Finsp_{O_2}*((P_{atm} - P_{H_2O}) - Pa_{CO_2}/Q_r)$"
        r" avec $P_{atm}=760 mmHg, \ P_{H_2O} = 47\ mmHg\ et\ Q_r \sim 0.8 $",
        fontsize=14,
        color=("tab:gray"),
    )
    ax = fig.add_subplot(111)

    ind = np.arange(4)  # class histo (insp-aerien-alveolaire-artériel)
    width = 0.2  # distance entre les plots
    for i, (k, casc) in enumerate(cascades.items()):
        label = f"g{str(int(k))}"
        if k == 0:
            label = "ref"
        ax.bar(
            ind + i * width,
            casc,
            width,
            alpha=0.6,
            label=label,
            edgecolor="w",
            linewidth=1,
        )
    ax.set_title(r"cascade de l' oxygène", color="tab:gray")
    ax.set_ylabel("pression partielle (mmHg)", color="tab:gray")
    ax.axhline(y=95, xmin=0.75, linewidth=2, alpha=1, color="red")
    ax.axhline(y=40, xmin=0.75, linewidth=2, alpha=1, color="blue")
    ax.axhline(y=159, xmin=0.01, xmax=0.25, linewidth=2, alpha=1, color="g")

    ax.set_xticks(ind + width)
    ax.set_xticklabels(("insp", "aérien", "alvéolaire", "artériel"))
    ax.legend()
    ax.tick_params(colors="tab:gray")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    for j, casc in enumerate(cascades.values()):
        for i, val in enumerate(casc):
            try:
                ax.annotate(
                    str(int(val)),
                    xy=(1, 2),
                    color="tab:grey",
                    xytext=(i + j * width, val + 5),
                    horizontalalignment="center",
                )
            except ValueError:
                continue

    if pyplot:
        # #fig.set.tight_layout(True)
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "cascO2"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)

    fig.text(0.99, 0.01, "plot_cascO2", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{nums=}", ha="left", va="bottom", alpha=0.4, size=12)

    return fig


def plot_cascO2Lin(
    gases: list[Any],
    nums: list,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot the O2 cascade.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    if type(nums) != list:
        nums = [
            nums,
        ]
    if nums[0] != 0:
        nums.insert(0, 0)
    cascades = {}
    for num in nums:
        if num in range(len(gases)):
            gas = gases[num]
            cascades[num] = gas.casc()
    if pyplot:
        fig = plt.figure(figsize=(14, 6))
    else:
        fig = Figure(figsize=(16, 8))
    # fig.suptitle(r'$Palv_{0_2} = Finsp_{O_2}*((P_{atm} - P_{H_2O}) - Pa_{CO_2}/Q_r)$'
    # ' avec $P_{atm}=760 mmHg, \ P_{H_2O} = 47\ mmHg\ et\ Q_r \sim 0.8 $', fontsize=14)
    ax = fig.add_subplot(111)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for i, (k, val) in enumerate(cascades.items()):
        label = f"gas {int(k)}"
        if k == 0:
            label = "ref"
        ax.plot(val, "o-.", label=label, linewidth=2, ms=10, alpha=0.8)
    ax.set_title(r"cascade de l'oxygène", alpha=0.5)
    ax.set_ylabel("pression partielle (mmHg)", alpha=0.5)
    ax.axhline(y=95, xmin=0.9, linewidth=2, alpha=1, color="red")
    ax.axhline(y=40, xmin=0.9, linewidth=2, alpha=1, color="blue")
    ax.axhline(y=159, xmin=0.02, xmax=0.10, linewidth=2, alpha=1, color="g")
    # ax.set_xlabel
    ax.set_xticks(range(len(val)))
    ax.set_xticklabels(("insp", "aérien", "alvéolaire", "artériel"))
    ax.tick_params(colors="tab:gray")
    ax.legend()
    st1 = r"$Palv_{0_2} = Finsp_{O_2}*((P_{atm} - P_{H_2O}) - Pa_{CO_2}/Q_r)$"
    st2 = r" avec $P_{atm}=760 mmHg, \ P_{H_2O} = 47\ mmHg\ et\ Q_r \sim 0.8 $"
    ax.text(0, 50, st1 + st2, fontsize=14, alpha=0.6)
    for casc in cascades.values():
        for i, val in enumerate(casc):
            try:
                ax.annotate(str(int(val)), xy=(i + 0.1, val), alpha=0.6)
            except ValueError:
                print("plot_cascO2Lin some values are missing")
                logging.warning("plot_cascO2Lin some values are missing")
                continue
    # fig.set.tight_layout(True)
    if pyplot:
        fig.tight_layout()
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "cascO2"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(0.99, 0.01, "plot_cascO2Lin", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{nums=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# ------------------------------------
def plot_GAa(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot alveolo-arterial gradient.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure

    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    if len(gases) > 1:
        casc = gases[num].casc()
    else:
        casc = gases[0].casc()
    gAa = casc[-2] - casc[-1]

    if pyplot:
        fig = plt.figure(figsize=(14, 3))
    else:
        fig = Figure(figsize=(14, 3))
    ax = fig.add_subplot(111)
    ax.axhline(0, color="tab:gray")
    ax.plot(
        [5, 15],
        [0, 0],
        label="line 1",
        linewidth=5,
        color="tab:blue",
        marker="d",
        markersize=10,
    )
    ax.plot([gAa], [0], "v-", color="tab:red", markersize=32, alpha=0.8)  # GAa
    st = "gradient alvéolo-artériel ($Palv_{O_2} - Pa_{O_2}$) "
    ax.set_title(st, backgroundcolor="w", color="tab:grey")
    ax.get_yaxis().set_visible(False)
    print("plot_GAa : ", casc[-2] - casc[-1], gAa)
    if gAa > 25:
        ax.set_xlim([0, gAa + 10])
    else:
        ax.set_xlim([0, 30])
    for spine in ["left", "top", "right", "bottom"]:
        ax.spines[spine].set_visible(False)
    #    ax.grid()
    ax.axes.tick_params(colors="tab:gray")
    # fig.set.tight_layout(True)
    if pyplot:
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "Gaa"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(0.99, 0.01, "plot_GAa", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# ------------------------------------
def plot_ratio(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot the ratio O2insp / PaO2.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure

    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    gas = gases[num]
    ratio = gas.po2 / gas.fio2
    # mes['po2'] / mes['fio2']

    if pyplot:
        fig = plt.figure(figsize=(14, 3))
    else:
        fig = Figure(figsize=(14, 3))
    ax = fig.add_subplot(111)
    ax.axhline(0, color="tab:grey")
    ax.plot(
        [100, 200],
        [0, 0],
        "tab:red",
        label="line 1",
        linewidth=2,
        marker="d",
        markersize=10,
    )
    ax.plot(
        [200, 300],
        [0, 0],
        "tab:orange",
        label="line 1",
        linewidth=4,
        marker="d",
        markersize=10,
    )
    ax.plot(
        [300, 500],
        [0, 0],
        "tab:blue",
        label="line 1",
        linewidth=6,
        marker="d",
        markersize=10,
    )
    ax.plot([ratio], [0], "rv-", markersize=32, markeredgecolor="k")  # ratio
    st = r"ratio $Pa_{O_2}\ /\ Fi_{O_2}$"
    ax.set_title(st, backgroundcolor="w", color="tab:gray")
    ax.yaxis.set_visible(False)
    #    ax.plot(300, 0, 'tab:blue', label='line 1', linewidth=1)

    ax.text(
        150, -0.025, r"ALI", fontsize=18, color="tab:red", horizontalalignment="center"
    )
    ax.text(
        250,
        -0.025,
        r"ARDS",
        fontsize=18,
        color="tab:orange",
        horizontalalignment="center",
    )
    ax.text(
        400,
        -0.025,
        r"norme",
        fontsize=18,
        color="tab:blue",
        horizontalalignment="center",
    )
    # ax.grid()
    ax.axes.tick_params(colors="tab:gray")
    for spine in ["left", "top", "right", "bottom"]:
        ax.spines[spine].set_visible(False)
    # fig.set.tight_layout(True)
    if pyplot:
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "ratio"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(0.99, 0.01, "plot_ratio", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# ------------------------------------
def plot_GAaRatio(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot alveolo-arterial gradient.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    gas = gases[num]
    casc = gas.casc()
    gAa = casc[-2] - casc[-1]
    ratio = gas.po2 / gas.fio2

    if pyplot:
        fig = plt.figure(figsize=(14, 6))
    else:
        fig = Figure(figsize=(14, 6))
    #    fig.suptitle("quantification du passage alvéolo-capillaire")
    ax = fig.add_subplot(211)
    ax.axhline(0, color="tab:grey")
    ax.plot(
        [5, 15],
        [0, 0],
        label="line 1",
        linewidth=4,
        color="tab:blue",
        marker="d",
        markersize=10,
    )
    ax.plot(
        [gAa], [0], "v-", color="tab:red", markersize=32, markeredgecolor="k"
    )  # GAa
    st = "gradient alvéolo-artériel ($PA_{O_2} - Pa_{O_2}$)"
    ax.set_title(st, y=0.8, backgroundcolor="w", color="tab:gray")
    print("gAa=", gAa)
    if gAa > 25:
        ax.set_xlim([0, gAa + 10])
    else:
        ax.set_xlim([0, 30])

    ax = fig.add_subplot(212)
    ax.axhline(0, color="tab:grey")
    ax.plot(
        [100, 200],
        [0, 0],
        "tab:red",
        label="line 1",
        linewidth=2,
        marker="d",
        markersize=10,
    )
    ax.plot(
        [200, 300],
        [0, 0],
        "tab:orange",
        label="line 1",
        linewidth=4,
        marker="d",
        markersize=10,
    )
    ax.plot(
        [300, 500],
        [0, 0],
        "tab:blue",
        label="line 1",
        linewidth=6,
        marker="d",
        markersize=10,
    )
    ax.plot([ratio], [0], "rv-", markersize=32, markeredgecolor="k")  # ratio
    st = "ratio $ Pa_{O_2} / Fi_{O_2}$"
    ax.set_title(st, y=0.8, backgroundcolor="w", color="tab:gray")
    ax.plot(300, 0, "tab:blue", label="line 1", linewidth=1)
    ax.text(
        150, -0.025, r"ALI", fontsize=18, color="tab:red", horizontalalignment="center"
    )
    ax.text(
        250,
        -0.025,
        r"ARDS",
        fontsize=18,
        color="tab:orange",
        horizontalalignment="center",
    )
    ax.text(
        400,
        -0.025,
        r"norme",
        fontsize=18,
        color="tab:blue",
        horizontalalignment="center",
    )
    for ax in fig.get_axes():
        ax.axes.tick_params(colors="tab:gray")
        ax.get_yaxis().set_visible(False)
        # ax.grid(True)
        for spine in ["left", "top", "right", "bottom"]:
            ax.spines[spine].set_visible(False)
    # fig.set.tight_layout(True)
    if pyplot:
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "GAaRatio"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(0.99, 0.01, "plot_GAaRatio", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# ------------------------------------
def plot_RatioVsFio2(
    mes: dict[Any, Any],
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot ratio vs FIO2.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    paO2 = mes["po2"]
    fiO2 = mes["fio2"]

    if pyplot:
        fig = plt.figure(figsize=(14, 4))
    else:
        fig = Figure(figsize=(14, 4))

    fig.suptitle("$Fi_{O_2}$ effect ( trop simple pour être vrai ? )")
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.7])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    # O2Range = np.linspace(1, 200, 200)
    paO2Range = np.linspace(100, 500, 200)
    fiO2Range = np.linspace(0.2, 1, 200)

    ax.plot(paO2Range, fiO2Range)
    ax.plot([100, 100], [0, 1], "tab:red", linewidth=8, alpha=0.4)  # ref
    ax.plot([40, 40], [0, 1], color="tab:blue", linewidth=26, alpha=0.4)
    ax.plot([50, 500], [0.2, 0.2], "tab:gray", linewidth=6, alpha=0.4)
    ax.plot([50, paO2], [fiO2, fiO2], "tab:gray", linewidth=1)  # mes
    ax.plot([paO2, paO2], [0, fiO2], "tab:gray", linewidth=1)
    ax.plot(paO2, fiO2, "o-", color="tab:red", markersize=22)  # PaCO2, FiO2

    ax.set_xlabel(r"$Pa_{O_2}$")
    ax.set_ylabel(r"$Fi_{O_2}$")
    ax.set_title(r"$Fi_{O_2}\ /\ Pa_{O_2}$", y=0.8, fontsize=30)
    ax.set_ylim([0, 1])
    ax.set_xlim([50, 500])
    ax.grid()

    if pyplot:
        # ##fig.set.tight_layout(True)
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "ratioVsFio2"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(
        0.99, 0.01, "plot_RatioVsFio2", ha="right", va="bottom", alpha=0.4, size=12
    )
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# --------------------------------------
def plot_satHb(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot ratio vs FIO2.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    gas = gases[num]
    species = gas.spec
    paO2 = gas.po2
    if paO2 > 200:
        O2max = paO2 + 50
    else:
        O2max = 200
    O2Range = np.arange(1, O2max)

    if species is None:
        logging.warning(f"{species=} is not defined")

    sat = satHbO2(species, paO2)

    if pyplot:
        fig = plt.figure(figsize=(10, 8))
    else:
        fig = Figure(figsize=(10, 8))

    fig.suptitle(
        species + " $SatHb_{O_2}$", fontsize=24, backgroundcolor="w", color="tab:gray"
    )

    ax = fig.add_subplot(111)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    ax.plot([100, 100], [0, 110], "tab:red", linewidth=8, alpha=0.4)  # line ref
    ax.plot([40, 40], [0, 110], color="tab:blue", linewidth=26, alpha=0.4)
    ax.plot(O2Range, satHbO2(species, O2Range), linewidth=2)  # mesure
    ax.plot([paO2, paO2], [0, sat], "tab:gray", linewidth=1)
    ax.plot([0, paO2], [sat, sat], "tab:gray", linewidth=1)

    ax.plot(paO2, sat, "o-", color="tab:red", markersize=32, alpha=0.8)
    #    st = "$Pa_{O_2}$ = "+ str(paO2)+ " mmHg"+ "\n"+ "$SatHb_{O_2}$ = " \
    #    + "{:.1f}".format(sat)+" %"
    st1 = "$Pa_{O_2}$ = " + str(paO2) + " mmHg"
    st2 = "$SatHb_{O_2}$' = " + f"{sat:.1f}%"
    ax.text(100, 80, st1 + "\n" + st2, color="tab:gray")
    ax.set_ylabel("satHb (%)", color="tab:grey")
    ax.set_xlabel(r"$P_{O_2}$ (mmHg)", color="tab:gray")
    ax.set_ylim([0, 110])
    # ax.grid()
    ax.axes.tick_params(colors="tab:gray")
    lims = ax.get_ylim()
    ax.set_ylim(0, lims[1])
    lims = ax.get_xlim()
    ax.set_xlim(0, lims[1])
    #    #fig.set.tight_layout(True)
    if pyplot:
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "satHb"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(0.99, 0.01, "plot_satHb", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# --------------------------------------
def plot_CaO2(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot CaO2.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    gas = gases[num]
    species = gas.spec
    paO2 = gas.po2
    hb = gas.hb
    if paO2 > 200:
        O2max = paO2 + 50
    else:
        O2max = 200
    O2Range = np.arange(1, O2max)
    contO2 = caO2(species, hb, paO2)

    if pyplot:
        fig = plt.figure(figsize=(10, 8))
    else:
        fig = Figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.set_title(species + r"$\ Ca_{O_2}$", color="tab:grey")

    ax.plot([100, 100], [0, 2500], "tab:red", linewidth=6, alpha=0.5)  # line ref
    ax.plot([40, 40], [0, 2500], color="tab:blue", linewidth=26, alpha=0.5)
    ax.plot([paO2, paO2], [0, contO2], "tab:gray", linewidth=1)  # mesure
    ax.plot([0, paO2], [contO2, contO2], "tab:gray", linewidth=1)
    st1 = "$Pa_{O_2}$ = " + str(paO2) + " $mmHg$"
    st2 = "$Ca_{O_2}$ = " + "{:.1f}".format(contO2) + " $ml/l$"
    ax.text(130, 1200, st1 + "\n" + st2, color="tab:gray")
    eq = r"$Ca_{O_2} = 1.36*satHb_{O_2}* [Hb] \ +\ 0.003*Pa_{O_2}$"
    ax.text(50, 2500, eq, backgroundcolor="w", color="tab:grey")
    ax.plot(O2Range, caO2(species, hb, O2Range), linewidth=2)  # ref
    ax.plot(O2Range, 0.00 * O2Range)
    ax.plot(paO2, contO2, "o-", color="tab:red", markersize=22, alpha=0.8)
    ax.set_ylabel(r"$Ca_{O_2}\ (ml/l)$", color="tab:gray")
    ax.set_xlabel(r"$P_{O_2}$", color="tab:gray")
    # ax.set_xlim([10, 200])
    # ax.grid()
    ax.axes.tick_params(colors="tab:gray")
    lims = ax.get_ylim()
    ax.set_ylim(0, lims[1])
    lims = ax.get_xlim()
    ax.set_xlim(0, lims[1])
    # fig.set.tight_layout(True)
    if pyplot:
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "caO2"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(0.99, 0.01, "plot_CaO2", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# --------------------------------------
def plot_varCaO2(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot CaO2 and CaO2 variation (slope).

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    gas = gases[num]
    species = gas.spec
    paO2 = gas.po2
    hb = gas.hb
    if paO2 > 200:
        O2max = paO2 + 50
    else:
        O2max = 200
    O2Range = np.arange(1, O2max)
    sat = satHbO2(species, paO2)

    if pyplot:
        fig = plt.figure(figsize=(10, 8))
    else:
        fig = Figure(figsize=(10, 8))
    st = species + r" ( $SatHb_{O_2} \ et \ \Delta SatHb_{O_2}$)"
    fig.suptitle(st, fontsize=24, backgroundcolor="w", color="tab:gray")

    ax1 = fig.add_subplot(111)  # ax1
    ax1.get_yaxis().tick_left()
    ax1.plot([100, 100], [0, 110], "tab:red", linewidth=10, alpha=0.5)  # line ref
    ax1.plot([40, 40], [0, 110], color="tab:blue", linewidth=26, alpha=0.5)
    ax1.plot(
        O2Range, satHbO2(species, O2Range), linewidth=2, color="tab:blue"
    )  # mesure
    ax1.plot([paO2, paO2], [0, sat], "tab:gray", linewidth=1)
    ax1.plot([0, paO2], [sat, sat], "tab:gray", linewidth=1)
    ax1.plot(paO2, sat, "o-", color="tab:red", markersize=22, alpha=0.7)
    ax1.set_ylabel("satHb (%)", color="tab:blue")
    ax1.set_xlabel(r"$P_{O_2}$", color="tab:gray")
    ax1.set_ylim(0, 100)

    ax2 = ax1.twinx()
    ax2.get_yaxis().tick_right()
    ax2.plot(
        O2Range,
        ((caO2(species, hb, O2Range + 1) - caO2(species, hb, O2Range))),
        color="tab:green",
    )
    ax2.plot(
        paO2,
        caO2(species, hb, paO2 + 1) - caO2(species, hb, paO2),
        "o-",
        color="tab:red",
        markersize=22,
        alpha=0.7,
    )
    for tl in ax2.get_yticklabels():
        tl.set_color("tab:green")
    ax2.set_ylabel("variation de CaO2 par variation de PO2", color=("tab:green"))
    #    ax2.set_xlabel(r'$P_{O_2}$')
    for ax in fig.get_axes():
        ax.axes.tick_params(colors="tab:gray")
        # ax.grid()
        for spine in ["left", "top", "right"]:
            ax.spines[spine].set_visible(False)
    # fig.set.tight_layout(True)
    if pyplot:
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "varCaO2"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(0.99, 0.01, "plot_varCaO2", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# --------------------------------------
def plot_hbEffect(
    gases: list[Any],
    num: int,
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot CaO2 for several Hb contents.

    Parameters
    ----------
    gases : list
        list of bg.Gas objects
    num : int
        location in the list.
    path : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    gas = gases[num]
    species = gas.spec
    paO2 = gas.po2
    hb = gas.hb
    if paO2 > 200:
        O2max = paO2 + 50
    else:
        O2max = 200
    O2Range = np.arange(1, O2max)
    contO2 = caO2(species, hb, paO2)

    if pyplot:
        fig = plt.figure(figsize=(10, 8))
    else:
        fig = Figure(figsize=(10, 8))
    st = "Hb effect (" + species + r" $Ca_{O_2}, \ (Hb = 5\ to \ 20) $ )"
    fig.suptitle(st, backgroundcolor="w", color="tab:gray")
    ax = fig.add_subplot(111)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.plot([100, 100], [0, 3000], "tab:red", linewidth=8, alpha=0.5)
    ax.plot([40, 40], [0, 3000], color="tab:blue", linewidth=26, alpha=0.5)
    for nHb in range(5, 20, 2):
        ax.plot(O2Range, caO2(species, nHb, O2Range), alpha=0.9)
    ax.plot([0, paO2], [contO2, contO2], "tab:gray", linewidth=1)
    ax.plot([paO2, paO2], [0, contO2], "tab:gray", linewidth=1)
    ax.plot(paO2, contO2, "o-", color="tab:red", markersize=22, alpha=0.8)
    ax.set_ylabel(r"$Ca_{O_2} (ml/l)$", color="tab:gray")
    ax.set_xlabel(r"$P_{O_2} \ (mmHg)$", color="tab:gray")
    ax.axes.tick_params(colors="tab:gray")
    ax.set_xlim([10, O2max])
    # ax.grid()
    lims = ax.get_ylim()
    ax.set_ylim(0, lims[1])
    # fig.set.tight_layout(True)
    if pyplot:
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "hBEffect"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(0.99, 0.01, "plot_hbEffect", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# --------------------------------------
def plot_satHorseDog(
    savedir: Optional[str] = None,
    ident: str = "",
    saveit: bool = False,
    pyplot: bool = True,
) -> plt.Figure:
    """
    Plot satHb horse and dog.

    Parameters
    ----------
    savedir : str
        path to save.
    ident : str, optional (default is "")
        string to identify in the save name.
    saveit : bool, optional (default is False)
        to save or not to save
    pyplot : bool, optional (default is False)
        True: return a pyplot,    else a Figure obj

    Returns
    -------
    fig : plt.Figure or matplotlib.Figure
    """
    if savedir is None:
        savedir = os.path.expanduser("~")
    if pyplot:
        fig = plt.figure(figsize=(10, 8))
    else:
        fig = Figure(figsize=(10, 8))

    fig.suptitle("$SatHb_{O_2}$ vs $P_{O_2}$", fontsize=24, color="tab:gray")
    # fig, ax = plt.subplots()
    PO2 = np.arange(1, 160)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    # ax.grid()
    ax.plot(PO2, satHbO2("horse", PO2), label="Horse", linewidth=2)
    ax.plot(PO2, satHbO2("dog", PO2), label="Dog", linewidth=2)
    ax.plot([100, 100], [0, 100], color="tab:red", linewidth=10, alpha=0.5)
    ax.plot([40, 40], [0, 100], color="tab:blue", linewidth=26, alpha=0.5)
    ax.legend(loc=4)
    #    plt.legend(loc=4)
    ax.set_xlabel(r"$P_{O_2}$", color="tab:gray")
    ax.set_ylabel(r"$SatHb_{O_2}$", color="tab:gray")
    ax.set_xlim(10, 160)

    if pyplot:
        # #fig.set.tight_layout(True)
        plt.show()
        if saveit:
            name = os.path.join(savedir, (str(ident) + "satHorseDog"))
            name = os.path.expanduser(name)
            saveGraph(name, ext="png", close=True, verbose=True)
    fig.text(
        0.99, 0.01, "plot_satHorseDog", ha="right", va="bottom", alpha=0.4, size=12
    )
    fig.text(0.01, 0.01, f"{num=}", ha="left", va="bottom", alpha=0.4, size=12)
    return fig


# -----------------------------------------------------------------------------
def showPicture(
    files: list[str], dirname: Optional[str] = None, title: str = ""
) -> plt.Figure:
    """
    To include a picture.

    Parameters
    ----------
    files : list[str]
        a list of file names.
    folderpath : str, optional (default is "~")
        the directory path
    title : str, optional (default is "")
        title to add to the display

    Returns
    -------
    plt.Figure

    """
    if dirname is None:
        dirname = "~"
    dirname = os.path.expanduser(dirname)
    file = os.path.join(dirname, files[0])
    if not os.path.isfile(file):
        print("file doesn't exist", file)
        return plt.Figure()
    fig = plt.figure(figsize=(12, 6))
    fig.suptitle(title)
    if len(files) == 1:
        file = os.path.join(dirname, files[0])
        ax = fig.add_subplot(111)
        # im = plt.imread(file)
        im = mpimg.imread(file)
        ax.imshow(im)
        ax.axis("off")
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        fig.tight_layout()
        return fig
    elif len(files) == 2:
        for i, item in enumerate(files):
            ax = fig.add_subplot(1, 2, i + 1)
            file = os.path.join(dirname, item)
            im = plt.imread(file)
            ax.imshow(im)
            ax.axis("off")
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
        fig.tight_layout()
        return fig
    else:
        print("can only plot two images")
    return fig


# -----------------------------------------------------------------------------
def saveGraph(
    filename: str, ext: str = "png", close: bool = True, verbose: bool = True
) -> None:
    """
    Save a figure from pyplot.

    Parameters
    ----------
    filename : string
        The path (and filename, without the extension) to save the
        figure to.
    ext : string (default='png')
        The file extension. This must be supported by the active
        matplotlib backend (see matplotlib.backends module). Most
        backends support 'png', 'pdf', 'ps', 'eps', and 'svg'.
    close : boolean (default=True)
        Whether to close the figure after saving. If you want to save
        the figure multiple times (e.g., to multiple formats), you
        should NOT close it in between saves or you will have to
        re-plot it.
    verbose : boolean (default=True)
        Whether to print information about when and where the image
        has been saved.
    """
    # Extract the directory and filename from the given path
    dirname = os.path.dirname(filename)
    file = os.path.split(filename)[1] + "." + ext.strip(".")
    if dirname == "":
        dirname = "."
    # If the directory does not exist, create it
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    # The final path to save to
    savedir = os.path.join(dirname, file)
    if verbose:
        print(f"Saving figure to {savedir} ...")
    # Actually save the figure
    plt.savefig(savedir)
    # Close it
    if close:
        plt.close()
    if verbose:
        print("Done")


# %%
if __name__ == "__main__":
    import trainingData

    data_df = trainingData.load_data()
    gases, gasesV = trainingData.build_gases(data_df)
    num = np.random.randint(len(gases))
    funcs: list[Callable] = [
        plot_display,
        plot_morpion,
        plot_acidbas,
        plot_o2,
        plot_ventil,
        plot_satHb,
        plot_cascO2,
        plot_hbEffect,
        plot_varCaO2,
        plot_pieCasc,
        plot_cascO2,
        plot_cascO2Lin,
        plot_GAa,
        plot_GAaRatio,
        plot_ratio,
    ]
    # %%
    for func in funcs:
        func(gases, num)
