#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:44:05 2022.

To load an example file.

@author: cdesbois
"""


import os
import logging
from typing import Any

import pandas as pd

import bgplot


def load_data(filename: str = None) -> pd.DataFrame:
    """
    Load an example csv file.

    Parameters
    ----------
    filename : str, optional (default is None)
        a csv file containing ['spec', 'hb', 'fio2', 'ph', 'pco2', 'hco3'] columns

    Returns
    -------
    df : pandas DataFrame
        the loaded data.

    """
    if filename is None:
        filename = os.path.join("data", "example.csv")
    df = pd.read_csv(filename, sep="\t")
    for col in df.columns:
        try:
            df[col] = df[col].astype(str)
            df[col] = df[col].apply(lambda x: x.replace(",", "."))
            df[col] = df[col].astype(float)
        except ValueError:
            logging.warning(f"column {col} can not be converted to float")
            df[col] = df[col].astype(str)
    return df


def build_gases(df: pd.DataFrame) -> tuple[list[Any], dict[str, Any]]:
    """
    Build gases from an example file.

    Parameters
    ----------
    df : pd.DataFrame
        containing ['spec', 'hb', 'fio2', 'ph', 'pco2', 'hco3'] columns.

    Returns
    -------
    tuple[list[Any], dict[str, Any]]
        list of bgplot gasobjet & list of dictionary of the data.

    """
    # initial values
    gases, gasesV = [], {}
    g0 = bgplot.Gas()
    gases.append(g0)
    gasesV["g0"] = g0.values()

    for i, row in df.iterrows():
        dico = row.to_dict()
        g = bgplot.Gas(**dico)
        gases.append(g)
        gasesV["g+i"] = dico
    return gases, gasesV


data_df = load_data()
gases, gasesV = build_gases(data_df)
