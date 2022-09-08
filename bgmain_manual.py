#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:23:33 2022.

For manual use of the plotting.


@author: cdesbois
"""

import os
import sys
import faulthandler
import logging
from typing import Optional
from typing import Tuple, Any, List, Dict, Callable

# from importlib import reload
from socket import gethostname
from time import localtime, strftime
import datetime

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QFileDialog

import bgplot

logfile = os.path.expanduser(os.path.join("~", "blood_gases.log"))
logging.basicConfig(
    level=logging.INFO,
    force=True,
    format="%(levelname)s:%(funcName)s:%(message)s",
    filename=logfile,
    filemode="w+",
    # handlers=[logging.FileHandler(logfile)],
)


class Bunch(dict):
    """Create a Bunch class."""

    def __getattribute__(self, key: str) -> None:
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key: str, value: str) -> None:
        self[key] = value


# buiding the paths_b
def build_path() -> Any:
    """
    Build variable paths_b (Bunch class).

    Return
    ------
        bunch, attributes: locations (root, data, record, save, pict)
    """
    paths_bunch = Bunch()
    root = "~"
    # panaPortableEnva
    if gethostname() == "UC-0514":
        print("pana")
        if sys.platform == "linux":
            print("panaLinux")
            root = os.path.join("/mnt", "wlShared")
        if sys.platform == "win32":
            print("panaWindows")
            root = "E:/"
    # pcBureauUnic
    if gethostname() == "PC-Chris-linux":
        root = os.path.join("/mnt", "hWin", "Chris")
    paths_bunch.root_ = root
    # recordings
    if sys.platform == "darwin":  # mac
        base = ["enva", "clinique", "recordings"]
        base.insert(0, root)
        records = os.path.join(*base)
        # folder = 'onDellRecorded'
        # folder = 'onPanaRecorded'
        folder = "onPanelPcRecorded"

        paths_bunch.record_ = records
        paths_bunch.data_ = os.path.join(records, "anesthRecords", folder)
        paths_bunch.save_ = os.path.join(records, "casClin", "buildingCorner")
        # path.sFig = os.path.join(path['save'], 'fig')
        # path.sBg = os.path.join(path['save'], 'bg')
        paths_bunch.pict_ = "~/enva/illustrations/drawings/respi/shuntDS"

    if gethostname() == "UC-0514":  # on pana (windows or linux)
        paths_bunch.data_ = os.path.join(root, "monitorData")
        paths_bunch.save_ = os.path.join(root, "fig")
        os.chdir(paths_bunch.data_)
    return paths_bunch


def append_anesth_plot_path(paths_bunch: Any) -> None:
    """AnesthPlot module."""
    base = ["pg", "chrisPg", "enva", "spyder", "record"]
    base.insert(0, paths_bunch.root_)
    mod_path = os.path.expanduser(os.path.join(*base))
    # change the working directory
    if mod_path not in sys.path:
        sys.path.append(mod_path)
        print(f"added {mod_path} to the path")
    os.chdir(mod_path)


def append_blood_gases_path(paths_bunch: Any) -> None:
    """Bloodgases."""
    base = ["pg", "chrisPg", "enva", "spyder", "bg"]
    base.insert(0, paths_bunch.root_)
    mod_path = os.path.expanduser(os.path.join(*base))
    if mod_path not in sys.path:
        sys.path.append(mod_path)
        print(f"added {mod_path} to the path")


paths_b = build_path()
# append_anesth_plot_path(paths_b)
# append_blood_gases_path(paths_b)


def build_xcel_model(dirname: str = None) -> None:
    """
    Save a generic xlsx file to enter the blood gases data.

    Parameters
    ----------
    dirname : str, optional (default is None)
        the directory to save in
    Returns
    -------
    None.

    """
    base_dico = {
        "date": {0: "2021-10-20"},
        "heure": {0: "00:00:00"},
        "spec": {0: "horse"},
        "name": {0: "thename"},
        "num": {0: np.nan},
        "fio2": {0: np.nan},
        "etco2": {0: np.nan},
        "ph": {0: np.nan},
        "pco2": {0: np.nan},
        "hco3": {0: np.nan},
        "anGap": {0: np.nan},
        "tco2": {0: np.nan},
        "be": {0: np.nan},
        "po2": {0: np.nan},
        "hb": {0: np.nan},
        "sat": {0: np.nan},
        "Na": {0: np.nan},
        "K": {0: np.nan},
        "Cl": {0: np.nan},
    }
    df = pd.DataFrame(base_dico)
    file = str(datetime.date.today()).replace("-", "_") + "_bg.xlsx"
    if dirname is None:
        dirname = "~"
    filename = os.path.expanduser(os.path.join(dirname, file))
    df.to_excel(filename)
    print("builded a generic .xlsx file to enter the data")
    print(f"{filename=}")


def load_xcel_file(bgfilename: str) -> pd.DataFrame:
    """
    Load the excel file containing the blood gases values.

    Parameters
    ----------
    bgfilename : the filename
        fullname

    Returns
    -------
    bgdf : pd.DataFrame
        the data.

    """
    bgdf = pd.read_excel(bgfilename, parse_dates=[["date", "heure"]]).set_index(
        "date_heure"
    )
    return bgdf


def add_o2co2_toBg(bgdf: pd.DataFrame, monitortrend: pd.DataFrame) -> pd.DataFrame:
    """
    Extract o2 and co2 from a monitorTrend, and fill the bloodgases dataframe.

    Parameters
    ----------
    bgdf : pd.DataFrame
        the blood gases values.
    monitortrend : pd.DataFrame
        a corresponding monitorTrend record.

    Returns
    -------
    bgdf : pd.DataFrame
        the blood gases values.

    """
    df = monitortrend.data[["datetime", "o2insp", "co2exp"]].set_index("datetime")
    tdelta = datetime.timedelta(minutes=3)
    dt = bgdf.index[1]
    for dt in bgdf.index:
        o2insp, co2exp = df.loc[dt - tdelta : dt + tdelta].median()
        bgdf.loc[dt, ["fio2", "etco2"]] = o2insp, co2exp
        print(dt, o2insp, co2exp)
    return bgdf


# ----------------------------------------------- end config
# manual use:
# spec='horse', hb=12, fio2=0.21, po2=95, ph=7.4, pco2=40, hco3=24, etco2=38


def append_from_dico(
    dico: Optional[dict], gaslist: Optional[list] = None, gasvisu: Optional[dict] = None
) -> Tuple[list, dict]:
    """
    Manual entries for blood gases values.

    - create a new Gas obj
    - append it to the gasesList
    - add a new 'g+nb' in the gasesVDict

    Parameters
    ----------
        dico : dictionary
            {'spec':, 'hb':, 'fio2':, 'po2':, 'ph':, 'pco2':, 'hco3':, 'etco2':}
        gaslist : list
            list of gas objects
        gasvisu : dict
            dictionary to visualise gaslist content

    Return
    ------
        append in gaslist and gasvisu
    """
    if gaslist is None:
        gaslist = []
        print(f"{'-' * 20} builded new gaslist")
    if gasvisu is None:
        gasvisu = {}
        print(f"{'-' * 20} builded new gasvisu")
    if dico is None:
        # key_list = ['spec', 'hb', 'fio2', 'po2', 'ph', 'pco2', 'hco3', 'etco2']
        dico = dict(
            spec="horse", hb=12, fio2=0.21, po2=95, ph=7.4, pco2=40, hco3=24, etco2=38
        )
    # gas = bgplot.Gas(*[dico[item] for item in key_list])
    gas = bgplot.Gas(**dico)
    gaslist.append(gas)
    name = "g" + str(len(gaslist) - 1)
    gasvisu[name] = gas.__dict__
    print(f"{'-' * 15} added a new gas from dico")
    for k, v in dico.items():
        print(f"{k:>6s}= {v}")

    print(f"{'-' * 20} gaslist contains {len(gasvisu)} gases")
    return gaslist, gasvisu


def userinput_to_dico() -> Dict[str, Any]:
    """
    User input for blood gases.

    Return
    ------
    newdico : dict
    """
    date = strftime("%y:%m:%d", localtime())
    heure = strftime("%H:%M", localtime())

    full_dico: Dict[str, Any] = {
        "date": date,
        "heure": heure,
        "spec": "horse",
        "name": "toto",
        "num": "",
        "fio2": 0.21,
        "etco2": 38,
        "ph": 7.42,
        "pco2": 40,
        "hco3": 24,
        "anGap": 15,
        "tco2": 32,
        "po2": 95,
        "hb": 12,
        "Na": 140,
        "K": 3.5,
        "Cl": 110,
    }

    print("type the value and validate")
    newdico: Dict[str, Any] = {}
    for k, v in full_dico.items():
        if k in ["date", "heure", "spec", "name"]:
            # default value
            inp = input(k + "(" + str(v) + ") : ") or str(v)
        else:
            inp = input(k + "(" + str(v) + ") : ") or "0"
        inp = inp.replace(",", ".")
        try:
            value = float(inp)
            newdico[k] = value
        except ValueError:
            newdico[k] = str(inp)
    print(newdico)
    return newdico


# %% from file
faulthandler.enable()
app = QApplication(sys.argv)


def choosefile_gui(dirname: str = None) -> str:
    """Select a file via a dialog and return the (full) filename.

    Parameters
    ----------
    dirname : str
        location to place the gui ('generally paths['data']) else home

    Return
    ------
    fname[0] : str
        filename
    """
    global app

    if dirname is None:
        dirname = os.path.expanduser("~/enva/clinique/recordings/anesthRecords")
    ##########
    # print("define widget")
    # wid = QWidget()
    # print("show command")
    # wid.show()
    # print("define options")
    # options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
    print("define QFiledialog")
    fname = QFileDialog.getOpenFileName(
        None, "Select a file...", dirname, filter="All files (*)"
    )
    # FIXME directory=dirname not working
    print("return")
    if isinstance(fname, tuple):
        return fname[0]
    return str(fname)


def csv_to_df(filename: str) -> pd.DataFrame:
    """
    Append new gases from a csvFile to gases & gasesV.

    Parameters
    ----------
    filename : str
        paths to csvFile (
            delimiter = tab, oneLine per gas
            columns should be :
                key_list = ['spec', 'hb', 'fio2', 'po2', 'ph', 'pco2', 'hco3', 'etco2']

    Return
    ------
        df:  pad.DataFrame
    """
    key_list = ["spec", "hb", "fio2", "po2", "ph", "pco2", "hco3", "etco2"]
    # load file as pd.DataFrame
    df = pd.read_csv(filename, sep="\t", decimal=",")
    # adapt the columns
    cols = list(map(str.lower, df.columns))
    cols = [st.replace("+", "") for st in cols]
    cols = [st.replace("-", "") for st in cols]
    df.columns = cols
    df = pd.DataFrame(df)
    # rename if required
    corr_title = {"thb": "hb"}
    df.rename(columns=corr_title, inplace=True)

    # test for missing columns
    for item in key_list:
        if item not in df.columns:
            print(item, "is missing in the file")
            return pd.DataFrame()
    # change the NaN by default values
    ref = {
        "spec": "horse",
        "hb": 12,
        "fio2": 0.21,
        "po2": 95,
        "ph": 7.4,
        "pco2": 40,
        "hco3": 24,
        "etco2": 38,
    }
    for col in df.columns:
        if col in ref:
            if df[col].hasnans:
                print("there are missing values in ", col)
                print("they will be replaced by ", ref[col])
                df[col] = df[col].fillna(ref.get(col))
    return df


def df_append_to_gases(
    df: pd.DataFrame, gaslist: Optional[list] = None, gasvisu: Optional[dict] = None
) -> Tuple[list, dict]:
    """
    Append to gases.

    Parameters
    ----------
    df : pandas DataFrame
        the gas data.
    gas_list : list
        of Gas objects
    gas_visu : list
        of __dict__ of Gas Objects

    Returns
    -------
    gaslist : list
        of gases objects
    gasvisu : dict
        for visualisation

    """
    # initialise if empty
    if gaslist is None:
        gaslist, gasvisu = append_from_dico(None)
    # fill line by line
    for i in range(len(df)):
        newgaslist, newgasvisu = append_from_dico(
            df.iloc[i].to_dict(), gaslist=gaslist, gasvisu=gasvisu
        )
    print("_" * 15)
    print(f"added {i} gases to the gas list")
    return newgaslist, newgasvisu


# build the reference set (ie room air, normal lung, normal respiratory state)
gas_list, gas_visu = append_from_dico(None)


append = False
if append:
    if "file_name" not in dir():
        file_name = choosefile_gui(paths_b.data_)
    data_df = csv_to_df(file_name)
    gas_list, gas_visu = df_append_to_gases(data_df, gas_list, gas_visu)


# %%%%%%%%%%%%%% append values
# by user input

addgas = False
if addgas:
    # manual input
    adico = userinput_to_dico()
    if "data_df" not in dir():
        data_df = pd.DataFrame(adico, index=[0])
    else:
        data_df = data_df.append(adico, ignore_index=True)
    # to gas list
    append_from_dico(adico, gaslist=gas_list, gasvisu=gas_visu)

# %% csv file  NB paths_b.record = ~/enva/clinique/recordings
addgas = False
if addgas:
    file = "casClin/recrut/gas.csv"
    file = "data/180910_oops/180910oopsBg.csv"
    file = "casClin/hypoK/190416hypoKalemia/bg.csv"
    file = "data/190621poly/doc/190621polyBg.csv"
    file = "casClin/stabColic/doc/bg.csv"
    file_name = os.path.join(paths_b.record_, file)

    in_df = csv_to_df(file_name)
    for i in range(len(in_df)):
        append_from_dico(in_df.iloc[i].to_dict(), gaslist=gas_list, gasvisu=gas_visu)

# %% h5 file
addgas = False
if addgas:
    airline = "~/enva/clinique/recordings/data/200816_airline"
    paths_b.airline_ = airline

    in_df = pd.read_hdf(os.path.join(paths_b.airline_, "bg20_08_16.h5"))
    for i in range(len(in_df)):
        append_from_dico(in_df.iloc[i].to_dict(), gaslist=gas_list, gasvisu=gas_visu)
save = False
if save:
    file_name = os.path.join(
        paths_b.record_, "anesthRecords", "bloodGases", "bg200816_airline.xlsx"
    )
    in_df.to_excel(file_name)


# %% #%% to plot all the graphs
# (NB pyplot = True return a pyplot, False return a matplotnib Figure Obj)

plt.close("all")


def plot_figs(gases: list[Any], **kwargs: Any) -> plt.Figure:
    """
    Plot the gases.

    Parameters
    ----------
    gases : list of gases objects
    **kwargs : arguments to use the list
        'key' in ['clin', 'all'] : graphs to plot
        'num' (default =  1) : gas to plot
        'reverse' (True) : order of the plotting
        'save' (False)
        'ident' () : added to the name of the plot for reuse
        'pyplot' (True) pyplot or matplotlib.Figure
        'path' ('~/test') : to save
        'folder' ('fig') : added to the save path
        'name'('None') = id of the animal

    Returns
    -------
    figlist : list of plotted figures
    fignames : list of figures suptitles
    """
    # print(kwargs)
    params: Dict[str, Any] = {
        "key": "clin",
        "num": 1,
        "reverse": True,
        "save": False,
        "ident": "",
        "pyplot": True,
        "path": "~/test",
        "folder": "fig",
        "name": None,
    }
    params.update(kwargs)
    # functions list
    plot_dico: Dict[str, List[Callable]] = {
        "all": [
            bgplot.plot_display,
            bgplot.plot_morpion,
            bgplot.plot_acidbas,
            bgplot.plot_o2,
            bgplot.plot_ventil,
            bgplot.plot_satHb,
            bgplot.plot_cascO2,
            bgplot.plot_hbEffect,
            bgplot.plot_varCaO2,
            bgplot.plot_pieCasc,
            bgplot.plot_cascO2,
            bgplot.plot_cascO2Lin,
            bgplot.plot_GAa,
            bgplot.plot_GAaRatio,
            bgplot.plot_ratio,
        ],
        "clin": [
            bgplot.plot_display,
            bgplot.plot_morpion,
            bgplot.plot_acidbas,
            bgplot.plot_o2,
            bgplot.plot_ventil,
            bgplot.plot_satHb,
            bgplot.plot_CaO2,
            bgplot.plot_hbEffect,
            bgplot.plot_varCaO2,
            bgplot.plot_pieCasc,
            bgplot.plot_cascO2Lin,
            bgplot.plot_GAa,
            bgplot.plot_GAaRatio,
            bgplot.plot_ratio,
        ],
    }
    if params["reverse"]:
        # reverse the order of the display
        for kind in ["all", "clin"]:
            plot_dico[kind] = plot_dico[kind][::-1]
    key = params["key"]  # 'all' or 'key'
    if key in plot_dico:
        # clin or all
        func_list = plot_dico[key]
    else:
        # direct call
        all_names = [func.__name__ for func in plot_dico["all"]]
        if key in all_names:
            func_list = [func for func in plot_dico["all"] if func.__name__ == key]
        else:
            print("key shoud be in ", all_names)
            return plt.Figure()
    figlist = []
    fignames = []
    path = params["path"]
    ident = params["ident"]
    save = params["save"]
    pyplot = params["pyplot"]
    num = int(params["num"])  # :int
    name = params.get("name", None)
    for func in func_list:
        if func.__name__ == "plot_cascO2Lin":
            # this function needs a list of gases
            # measure + ref
            # fig = func(gases, [0, num], path, ident, save, pyplot)
            # all until measure
            fig = func(gases, list(range(num + 1)), path, ident, save, pyplot)
            # fig = item(gases, list(range(len(gases))), path, ident, save, pyplot)
        elif func.__name__ == "plot_cascO2":
            # this function needs a list of gases
            # measure + ref
            fig = func(gases, [0, num], path, ident, save, pyplot)
            # all measures
            # fig = item(gases, list(range(len(gases))), path, ident, save, pyplot)
        elif func.__name__ == "plot_pieCasc":
            fig = func(gases, num, path, ident="", save=save, pcent=True, pyplot=pyplot)
            fig = func(
                gases, num, path, ident="", save=save, pcent=False, pyplot=pyplot
            )
        else:
            fig = func(gases, num, path, ident, save, pyplot)
        figlist.append(fig)
        fignames.append(func.__name__.split("_")[-1])
    for fig in figlist:
        fig.text(0.99, 0.01, "bgPlot", ha="right", va="bottom", alpha=0.4, size=12)
        if name is None:
            fig.text(0.01, 0.01, "cDesbois", ha="left", va="bottom", alpha=0.4, size=12)
        else:
            fig.text(0.01, 0.01, name, ha="left", va="bottom", alpha=0.4, size=12)
    return figlist, fignames


def print_beamer_include(folder: str, figlist: list) -> None:
    """
    Print in console the beamer commands to include the generated plots.

    Parameters
    ----------
    folder : str
        the path inside the beamer folder
    fig_list: list
        the figure list
    """
    print("******** beamer commands *******")
    for fig in figlist:
        txt = os.path.join(folder, fig.split("_")[-1])
        one = r"\begin{frame}[plain]"
        two = r"\includegraphics[width=\linewidth]{%s}" % txt
        three = r"\end{frame}"
        print(one)
        print(two)
        print(three)
        print()


# (NB pyplot = True return a pyplot, False return a matplotnib Figure Obj)
# plt.close('all')
# num     = 1             # gas number (0 = ref, first=1)
# #num = len(gases) - 1
# reverse=False
# save    = False
# ident   = ''
# pyplot= True
# path = ''
# folder = 'bg/'    # location in the beamer folder

varDico: Dict[str, Any] = {
    "key": "clin",
    "num": 1,  # gas number (0 = ref, first=1)
    # num = len(gases) - 1
    "reverse": False,
    "save": False,
    "ident": "",
    "pyplot": True,
    "path": "",
    "folder": "bg/",  # location in the beamer folder
}

plot = False
if plot:
    fig_list, fig_names = plot_figs(gas_list, **varDico)
    print_beamer_include(varDico["folder"], fig_names)

# %% to plot the standart ventil figures
if plot:
    picts = [
        "alveoloCap.png",
        "alveolPhysio.png",
        "alveolDS.png",
        "alveolShuntFoncti.png",
    ]
    # pictPath = '/Users/cdesbois/enva/illustrations/shémas/respi/shuntDs'

    figure = bgplot.showPicture(picts[:2], paths_b.pict_)  # alvCap + physio
    figure = bgplot.showPicture(picts[2:], paths_b.pict_)  # dsShuntemail

# %% to plot from csv: (see libreOffice template)
csv = False
if csv:
    day = os.path.basename(file_name)[:6]
    in_df["heure"] = pd.to_datetime(day + " " + in_df.time)
    in_df["heureShift"] = in_df.heure.shift(1)
    in_df["delay"] = in_df.heure - in_df.heureShift
    in_df.delay = in_df.delay.apply(lambda x: x.seconds // 60).replace(np.nan, 0)
    # df.set_index('delay', inplace=True)

# %% display the evolution of the blood gases iono, ....

plt.close("all")


def plot_evol_o2co2(df: pd.DataFrame) -> plt.Figure:
    """
    Plot 02 and CO2 evolution.

    Parameters
    ----------
    df : pandas dataframe
        (index can be set to date_time)

    Returns
    -------
    fig : pyplot figure.
    """
    fig = plt.figure(figsize=(8, 4))
    fig.suptitle("respiratoire", color="tab:gray")
    # o2
    ax = fig.add_subplot(111)
    ax.plot(df.po2, "-o", color="tab:red", ms=10)
    ax.set_ylabel("$Pa 0_2$", color="tab:red")
    usual = [80, 112]
    spread = set(usual) | set(ax.get_ylim())
    lims = bgplot.round_lims(spread, 5)
    ax.set_ylim(lims)
    ax.spines["left"].set_color("tab:red")
    ax.tick_params(axis="y", colors="tab:red")
    ax.axhline(90, color="tab:red", linestyle="dashed", alpha=0.4, linewidth=3)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    # co2
    axT = ax.twinx()
    axT.plot(df.pco2, "-o", color="tab:blue", ms=10)
    axT.set_ylabel("$Pa C0_2$", color="tab:blue")
    usual = [36, 46]
    spread = set(usual) | set(axT.get_ylim())
    lims = bgplot.round_lims(spread, 5)
    axT.set_ylim(lims)
    # axT.set_ylim(min(spread), max(spread))

    axT.spines["right"].set_color("tab:blue")
    axT.tick_params(axis="y", colors="tab:blue")
    axT.axhline(40, color="tab:blue", linestyle="dashed", alpha=0.6, linewidth=3)
    for spine in ["top", "left"]:
        axT.spines[spine].set_visible(False)
    # gas_list = df.num.astype(int).astype(str).to_list()
    # gas_list = ['gas' + item for item in gas_list]
    for ax in fig.get_axes():
        ax.spines["top"].set_visible(False)
        ax.yaxis.set_major_locator(
            MaxNLocator(integer=True, nbins=5, steps=[1, 2, 5, 10])
        )

        # check if index is datetime
        if df.index.dtype != "<M8[ns]":
            ax.xaxis.set_ticks(np.arange(len(df)))
            # ax.xaxis.set_ticklabels(gas_list)
            ax.xaxis.set_ticklabels(df.heure)
        else:
            date_format = DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(date_format)
        ax.spines["bottom"].set_color("tab:gray")
        ax.tick_params(axis="x", colors="tab:gray")
    fig.tight_layout()
    return fig


def plot_acidobas(df: pd.DataFrame) -> plt.Figure:
    """
    Plot acido_basic informations.

    Parameters
    ----------
    df : pandas dataframe
        (index can be set to datetime)

    Returns
    -------
    None.
    """
    fig = plt.figure(figsize=(8, 4))
    fig.suptitle("acidoBasique", color="tab:gray")

    ax1 = fig.add_subplot(211)
    ax1.plot(df.ph, "-o", color="tab:gray", ms=10)
    ax1.set_ylabel("pH")
    ax1.axhspan(7.35, 7.45, alpha=0.3, color="tab:grey")
    usual = [7.34, 7.48]
    spread = set(usual) | set(ax1.get_ylim())
    lims = bgplot.round_lims(spread, 0.1)
    ax1.set_ylim(lims)
    ax1.yaxis.set_major_locator(
        MaxNLocator(integer=False, nbins=3, steps=[1, 2, 5, 10])
    )

    ax2 = fig.add_subplot(212)
    ax2.plot(df.pco2, "-o", color="tab:blue", ms=10)
    ax2.set_ylabel("$Pa CO_2$", color="tab:blue")
    usual = [36, 46]
    spread = set(usual) | set(ax2.get_ylim())
    lims = bgplot.round_lims(spread, 5)
    ax2.set_ylim(lims)
    ax2.spines["left"].set_color("tab:blue")
    ax2.tick_params(axis="y", colors="tab:blue")
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=3, steps=[1, 2, 5, 10]))
    for spine in ["top", "right"]:
        ax2.spines[spine].set_visible(False)

    ax3 = ax2.twinx()
    ax3.plot(df.hco3, "-o", color="tab:orange", ms=10)
    ax3.set_ylabel("$HCO_3$", color="tab:orange")
    usual = [22, 29]
    spread = set(usual) | set(ax3.get_ylim())
    lims = bgplot.round_lims(spread, 1)
    ax3.set_ylim(lims)
    ax3.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=3, steps=[1, 2, 5, 10]))
    ax3.spines["right"].set_color("tab:orange")
    ax3.tick_params(axis="y", colors="tab:orange")
    for spine in ["top", "left"]:
        ax3.spines[spine].set_visible(False)

    for ax in fig.get_axes():
        ax.spines["top"].set_visible(False)
        if df.index.dtype != "<M8[ns]":
            ax.xaxis.set_ticks(np.arange(len(df)))
            # ax.xaxis.set_ticklabels(gas_list)
            ax.xaxis.set_ticklabels(df.heure)
        else:
            date_format = DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(date_format)
        ax.spines["bottom"].set_color("tab:gray")
        ax.tick_params(axis="x", colors="tab:gray")
    ax1.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig


def plot_metabo(df: pd.DataFrame) -> plt.Figure:
    """
    Plot hco3- and anionGap over time.

    Parameters
    ----------
    df : pd.DataFrame
        the data

    Returns
    -------
    plt.Figure
    """
    fig = plt.figure(figsize=(8, 4))
    fig.suptitle("métabo", color="tab:gray")
    ax = fig.add_subplot(111)
    ax.plot(df.hco3, "-o", color="tab:orange", ms=10)
    ax.set_ylabel("$HCO_3$", color="tab:orange")
    usual = [22, 29]
    spread = set(usual) | set(ax.get_ylim())
    lims = bgplot.round_lims(spread, 1)
    ax.set_ylim(lims)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=3, steps=[1, 2, 5, 10]))
    ax.spines["left"].set_color("tab:orange")
    ax.tick_params(axis="y", colors="tab:orange")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    axT = ax.twinx()
    axT.plot(df.anGap, "-o", color="tab:cyan", ms=10)
    # usual = [130, 145]
    # spread = set(usual) | set(axT.get_ylim())
    # ax.set_ylim(min(spread), max(spread))
    axT.set_ylabel("anGap", color="tab:cyan")
    axT.spines["right"].set_color("tab:cyan")
    axT.tick_params(axis="y", colors="tab:cyan")
    usual = [5, 16]
    spread = set(usual) | set(axT.get_ylim())
    lims = bgplot.round_lims(spread, 2)
    axT.set_ylim(lims)
    axT.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=3, steps=[1, 2, 5, 10]))
    for spine in ["top", "left"]:
        axT.spines[spine].set_visible(False)
    for ax in fig.get_axes():
        ax.spines["top"].set_visible(False)
        if df.index.dtype != "<M8[ns]":
            ax.xaxis.set_ticks(np.arange(len(df)))
            # ax.xaxis.set_ticklabels(np.arange(len(df)))
            ax.xaxis.set_ticklabels(df.heure)
        else:
            date_format = DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(date_format)
        ax.spines["bottom"].set_color("tab:gray")
        ax.tick_params(axis="x", colors="tab:gray")
    fig.tight_layout()
    return fig


def plot_iono(df: pd.DataFrame) -> plt.Figure:
    """
    Plot Iono.

    Parameters
    ----------
    df : pandas.DataFrame
        the values

    Returns
    -------
    fig : plt.Figure

    """
    fig = plt.figure(figsize=(8, 4))
    fig.suptitle("iono", color="tab:gray")
    ax = fig.add_subplot(211)
    ax.plot(df.Na, "-o", color="tab:red", ms=10)
    # lims = ax.get_xlim()
    # ax.hlines(135, *lims, colors='r', alpha=0.5, linestyles='dashed')
    # ax.hlines(145, *lims, colors='r', alpha=0.5, linestyles='dashed')
    usual: list[float] = [136, 142]
    spread = set(usual) | set(ax.get_ylim())
    lims = bgplot.round_lims(spread, 5)
    ax.set_ylim(lims)
    ax.set_ylabel("$Na^+$", color="tab:red")
    ax.spines["left"].set_color("tab:red")
    ax.tick_params(axis="y", colors="tab:red")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    axT = ax.twinx()
    axT.plot(df.Cl, "-o", color="tab:blue", ms=10)
    axT.set_ylabel("$Cl^-$", color="tab:blue")
    usual = [98, 104]
    spread = set(usual) | set(axT.get_ylim())
    lims = bgplot.round_lims(spread)
    axT.set_ylim(lims)
    # lims = axT.get_xlim()
    # axT.hlines(110, *lims, colors='b', alpha=0.5, linestyles='dashed')
    # axT.hlines(95, *lims, colors='b', alpha=0.5, linestyles='dashed')
    axT.spines["right"].set_color("tab:blue")
    axT.tick_params(axis="y", colors="tab:blue")
    for spine in ["top", "left"]:
        axT.spines[spine].set_visible(False)

    ax2 = fig.add_subplot(212)
    ax2.plot(df.K, "-o", color="tab:purple", ms=10)
    ax2.set_ylabel("$K^+$", color="tab:purple")
    usual = [2.2, 4]
    spread = set(usual) | set(ax2.get_ylim())
    lims = bgplot.round_lims(spread, 1)
    ax2.set_ylim(lims)
    ax2.spines["left"].set_color("tab:purple")
    ax2.tick_params(axis="y", colors="tab:purple")
    for spine in ["top", "right"]:
        ax2.spines[spine].set_visible(False)

    ax2T = ax2.twinx()
    ax2T.plot(df.ph, "-o", color="tab:gray", ms=10)
    ax2T.set_ylabel("pH", color="tab:gray")
    usual = [7.34, 7.48]
    spread = set(usual) | set(ax2T.get_ylim())
    lims = bgplot.round_lims(spread, 0.2)
    ax2.set_ylim(lims)
    ax2T.spines["right"].set_color("tab:gray")
    ax2T.tick_params(axis="y", colors="tab:gray")
    for spine in ["top", "left"]:
        ax2T.spines[spine].set_visible(False)

    for ax in fig.get_axes():
        ax.spines["top"].set_visible(False)
        if df.index.dtype != "<M8[ns]":
            ax.xaxis.set_ticks(np.arange(len(df)))
            # ax.xaxis.set_ticklabels(np.arange(len(df)))
            ax.xaxis.set_ticklabels(df.heure)
        else:
            date_format = DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(date_format)
        ax.spines["bottom"].set_color("tab:gray")
        ax.tick_params(axis="x", colors="tab:gray")

    fig.tight_layout()
    return fig


def plot_hb(df: pd.DataFrame) -> plt.Figure:
    """
    Plot hb over time.

    Parameters
    ----------
    df : pd.DataFrame
        the data.

    Returns
    -------
    plt.Figure
    """
    fig = plt.figure(figsize=(8, 4))
    fig.suptitle("Hb", color="tab:gray")
    ax = fig.add_subplot(111)
    ax.plot(df.hb, "-o", color="tab:red")

    usual: List[float] = []
    spread = set(usual) | set(ax.get_ylim())
    lims = bgplot.round_lims(spread, 1)
    ax.set_ylim(lims)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=3, steps=[1, 2, 5, 10]))
    ax.set_ylabel("Hb", color="tab:red")
    ax.spines["left"].set_color("tab:red")
    ax.tick_params(axis="y", colors="tab:red")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
        if df.index.dtype != "<M8[ns]":
            ax.xaxis.set_ticks(np.arange(len(df)))
            # ax.xaxis.set_ticklabels(np.arange(len(df)))
            ax.xaxis.set_ticklabels(df.heure)
        else:
            date_format = DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(date_format)
    ax.spines["bottom"].set_color("tab:gray")
    ax.tick_params(axis="x", colors="tab:gray")
    fig.tight_layout()
    return fig


# %%
plot_evol = False
if plot_evol:
    plot_evol_o2co2(in_df)
    plot_acidobas(in_df)
    plot_metabo(in_df)
    plot_iono(in_df)
    plot_hb(in_df)
