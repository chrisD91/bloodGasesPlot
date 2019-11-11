#! /Volumes/USERS/cdesbois/anaconda/bin/python  ###########  /usr/bin/env python3
# -*- coding: utf-8 -*-

%reset -f
# clear all the previous data
#from IPython import get_ipython
#get_ipython().magic('reset -sf')

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from imp import reload
from socket import gethostname
from collections import OrderedDict
import os, sys
# ------------------------------------------
# buiding the path
def buildPath():
    """
    build path['root', 'data', 'utils', 'save']
    """
    path = {}
    root = '~'
    # panaPortableEnva
    if gethostname() == 'UC-0514':
        print('pana')
        if sys.platform == 'linux':
            print('panaLinux')
            root = os.path.join('/mnt', 'wlShared')
        if sys.platform == 'win32':
            print('panaWindows')
            root = 'E:/'
    # pcBureauUnic
    if gethostname() == 'PC-Chris-linux':
        root = os.path.join('/mnt', 'hWin', 'Chris')
    path['root'] = root

    # recordings
    if sys.platform == 'darwin':    # mac
        base = ['enva', 'clinique', 'recordings']
        base.insert(0, root)
        homePath = os.path.expanduser(os.path.join(*base))
        # folder = 'onDellRecorded'
#        folder = 'onPanaRecorded'
        folder = 'onPanelPcRecorded'
        path['data'] = os.path.join(homePath, 'anesthRecords', folder)
        path['save'] = os.path.join(homePath, 'casClin', 'buildingCorner')
        path['sFig'] = os.path.join(path['save'], 'fig')
        path['sBg'] = os.path.join(path['save'], 'bg')
        path['picts'] = '/Users/cdesbois/enva/illustrations/drawings/respi/shuntDS'

    if gethostname() == 'UC-0514':  # on pana (windows or linux)
        path['data'] = os.path.join(root, 'monitorData')
        path['save'] = os.path.join(root, 'fig')
        os.chdir(path['data'])
  
    return(path)

def appendUtils(paths):
    """utils module"""
    base = ['pg', 'utils']
    base.insert(0, paths['root'])
    modPath = os.path.expanduser(os.path.join(*base))
    print('modPath= ', modPath)
    # change the working directory
    if modPath not in sys.path:
        sys.path.append(modPath)
        print('added', modPath, ' to the path')

def anesthPlotPath(paths):
    """anesthPlot module """
    base = ['pg', 'chrisPg', 'enva', 'spyder', 'record']
    base.insert(0, paths['root'])
    modPath = os.path.expanduser(os.path.join(*base))
    # change the working directory
    if modPath not in sys.path:
        sys.path.append(modPath)
        print('added', modPath, ' to the path')
    os.chdir(modPath)


def bloodGasesPath(paths):
    """ bloodgases """
    base = ['pg', 'chrisPg', 'enva', 'spyder', 'bg']
    base.insert(0, paths['root'])
    modPath = os.path.expanduser(os.path.join(*base))
    if modPath not in sys.path:
        sys.path.append(modPath)
        print('added', modPath, ' to the path')

paths = buildPath()
appendUtils(paths)
anesthPlotPath(paths)
bloodGasesPath(paths)
import utils

import bgplot as bg
import anesthPlot as plot
import utils


gases, gasesV = [], {}

# manual use:
# spec='horse', hb=12, fio2=0.21, po2=95, ph=7.4, pco2=40, hco3=24, etco2=38

def appendFromDico(dico):
    """
    manual entries for blood gases values :
        - create a new Gas obj
        - append it to the gasesList
        - add a new 'g+nb' in the gasesVDict

    input: dictionary
    {'spec':, 'hb':, 'fio2':, 'po2':, 'ph':, 'pco2':, 'hco3':, 'etco2':}


    output : append in gases and gasV
    """
    global gases, gasesV
    keyList = ['spec', 'hb', 'fio2', 'po2', 'ph', 'pco2', 'hco3', 'etco2']
    valList = []
    # build the list of values
    for key in keyList:
        valList.append(dico[key])
    # create the bg obj and append to the gas list and gasV dictionary
    # g = bg.Gas(valList)             # TOFIX : list accepted as a list, not separated values
    spec    = dico['spec']
    hb      = dico['hb']
    fio2    = dico['fio2']
    po2     = dico['po2']
    ph      = dico['ph']
    pco2    = dico['pco2']
    hco3    = dico['hco3']
    etco2   = dico['etco2']

    g = bg.Gas(spec, hb, fio2, po2, ph, pco2, hco3, etco2)


#    g = bg.Gas('spec'= dico['spec'], 'hb' = dico['hb'], 'fio2' = dico['fio2'],
#               'po2' = dico['po2'], 'ph'= dico['ph'], 'pco2'= dico['pco2'],
#               'hco3' = dico['hco3'], 'etco2'= dico['etco2'])
    gases.append(g)
    name = 'g' + str(len(gases) - 1)
    gasesV[name] = g.__dict__
    print('*spec=', g.spec, '*hb=', g.hb, '*fio2= ', g.fio2,
          '*po2=', g.fio2, '*ph=', g.ph, '*pco2= ', g.pco2,
          '*hco3=', g.hco3, '*etco2=', g.etco2)

# reference set (ie room air, normal lung, normal respiratory state)
refDico = {'spec': 'horse', 'hb': 12, 'fio2': 0.21, 'po2': 95, 'ph': 7.4,
        'pco2': 40, 'hco3': 24, 'etco2': 38}

#dico = {'spec': 'horse', 'hb': 12, 'fio2': 0.5, 'po2': 106, 'ph': 7.44,
#        'pco2': 45, 'hco3': 24, 'etco2': 38}

def userInputToDico(refDico):
    """ 
    user input blood gases
    return a dictionary
    """
    dico={}
    for key in refDico:
        dico[key] = input(key +'(' + str(refDico[key])+ ') : ')
    for key in dico.keys():
        try:
            dico[key] = float(dico[key])
        except:
            pass
    print(dico)
    return(dico)

def loadCsvToDf(fileName):
    """
    append new gases from a csvFile
    input : csvFile, delimiter = tab, oneLine per gas
    append the gases to the lists (gases, gasesV)
    return a pandasDataFrame
    """
    keyList = ['spec', 'hb', 'fio2', 'po2', 'ph', 'pco2', 'hco3', 'etco2']
    # load file as pd.DataFrame
    df = pd.read_csv(fileName, sep='\t',decimal=',') 
    # test if the needed values are present
    for item in keyList:
        if item not in df.columns:
            print(item, 'is missing in the file')
            return
    # change the NaN by default values
    for col in df.columns:
        if col in refDico.keys():
            if df[col].hasnans:
                print('there are missing values in ', col)
                print('they will be replaced by ', refDico[col])
                df[col] = df[col].fillna(refDico[col])
#    for col in df.columns:
#        if col in refDico.keys():
#            df[col] = df[col].fillna(refDico[col])
#    # append in the gas list
#    for i in range(len(df)):
#        manualGasAdd(dict(df.iloc[i]))
#    print('added', i+1, 'gases')
    return df

def appendFromDf(df):
    """
    append the df values to the gas list
    """
    for i in range(len(df)):
        appendFromDico(dict(df.iloc[i]))
    print('added', i+1, 'gases')


# build the reference set
appendFromDico(refDico)

#%%%%%%%%%%%%%% append values
#%% manual
#adico = userInputToDico(refDico)
#appendFromDico(adico)

#%% from a file
#append from csv
fileName = '/Users/cdesbois/enva/clinique/recordings/casClin/recrut/gas.csv'
fileName = '/Users/cdesbois/enva/clinique/recordings/data/180910_oops/180910oopsBg.csv'
fileName = '/Users/cdesbois/enva/clinique/recordings/casClin/hypoK/190416hypoKalemia/bg.csv' 
fileName = '/Users/cdesbois/enva/clinique/recordings/data/190621poly/doc/190621polyBg.csv'
fileName = '/Users/cdesbois/enva/clinique/recordings/casClin/stabColic/doc/bg.csv'
df = loadCsvToDf(fileName)
#appendFromDf(df)

#%% #%% to plot all the graphs
# (NB pyplot = True return a pyplot, False return a matplotnib Figure Obj)

plt.close('all')
def plotFigs(gases, *args,  **kwargs):
    """
    plot the gases
    input = 'clin' or 'all', reverse: boolean to show the first plot in front
    return= figList = list of plotted figures
            figNames = list of figures suptitle
    """
    params={
            'key' : 'clin',
            'num' : 1,
            'reverse' : True,
            'save' : False,
            'ident' : '',
            'pyplot' : True,
            'path' : '~/test',
            'folder' : 'fig'
            }
    params.update(kwargs)
    #functions list
    plotDico = {
            'all': [bg.display, bg.morpion, bg.plot_acidbas, bg.plot_o2, \
               bg.plot_ventil, bg.plot_satHb, bg.plot_cascO2, \
               bg.plot_hbEffect, bg.plot_varCaO2, bg.plot_pieCasc, \
               bg.plot_cascO2, bg.plot_cascO2Lin, bg.plot_GAa, \
               bg.plot_GAaRatio, bg.plot_ratio],
            'clin' : [bg.display, bg.morpion, bg.plot_acidbas, bg.plot_o2, \
                bg.plot_ventil, bg.plot_satHb, bg.plot_CaO2, bg.plot_hbEffect,\
                bg.plot_varCaO2, bg.plot_pieCasc, bg.plot_cascO2Lin, bg.plot_GAa,\
                bg.plot_GAaRatio, bg.plot_ratio]
                }
    if params['reverse']:
        # reverse the order of teh display
        for kind in ['all', 'clin']:
            plotDico[kind] = plotDico[kind][::-1]
    key = params['key']
    if key in plotDico.keys():
        aList = plotDico[key]
    else:
        allNames = [n.__name__ for n in plotDico['all']]
        if key not in allNames:
            print('key shoud be in ', allNames)
            return
        else:
            aList = []
            for n in plotDico['all']:
                if key == n.__name__: 
                    aList.append(n)
    figList = []
    figNames = []
    path = params['path']
    ident = params['ident']
    save = params['save']
    pyplot = params['pyplot']
    num = params['num']
    for item in aList:
        if item.__name__  == 'plot_cascO2Lin':
            # this function needs a list of gases 
            # measure + ref
            fig = item(gases, [0, num], path, ident, save, pyplot)
            # all measures
            # fig = item(gases, list(range(len(gases))), path, ident, save, pyplot)
        elif item.__name__  == 'plot_cascO2':
            # this function needs a list of gases 
            # measure + ref
            fig = item(gases, [0, num], path, ident, save, pyplot)
            # all measures
            # fig = item(gases, list(range(len(gases))), path, ident, save, pyplot)
        elif item.__name__ == 'plot_pieCasc':
            fig = item(gases, num, path, ident='', save=save, percent=True, pyplot = pyplot)
            fig = item(gases, num, path, ident='', save=save, percent=False, pyplot = pyplot)
        else:
            fig = item(gases, num, path, ident, save, pyplot)
        figList.append(fig)
        figNames.append(item.__name__.split('_')[-1])
    return figList, figNames


def printBeamerInclude(folder, figList):
    """
    print in console the beamer commands to include the generated plots
    input : folder (the path inside the beamer folder)
    figList
    """
    print ('******** beamer commands *******')
    for fig in figList:
        txt = os.path.join(folder, fig.split('_')[-1])
        one = r'\begin{frame}[plain]'
        two = r'\includegraphics[width=\linewidth]{%s}' % txt
        three = r'\end{frame}' 
        print(one)
        print(two)
        print(three)
        print()

# (NB pyplot = True return a pyplot, False return a matplotnib Figure Obj)
#plt.close('all')
#num     = 1             # gas number (0 = ref, first=1)
##num = len(gases) - 1
#reverse=False
#save    = False
#ident   = ''
#pyplot= True
#path = ''
#folder = 'bg/'    # location in the beamer folder

varDico={
        'key':'clin',
        'num':1,             # gas number (0 = ref, first=1)
        #num = len(gases) - 1
        'reverse': False,
        'save'    :False,
        'ident'  : '',
        'pyplot' : True,
        'path' : '',
        'folder' : 'bg/'    # location in the beamer folder
        }

figList, figNames = plotFigs(gases, **varDico)
printBeamerInclude(varDico['folder'], figNames)

#%% to plot the standart ventil figures
picts = ['alveoloCap.png', 'alveolPhysio.png', 'alveolDS.png', 'alveolShuntFoncti.png']
#pictPath = '/Users/cdesbois/enva/illustrations/shémas/respi/shuntDs'

fig = bg.showPicture(picts[:2], paths['picts'])   # alvCap + physio
fig = bg.showPicture(picts[2:], paths['picts'])   # dsShuntemail

#%% to plot from csv: (see libreOffice template)
day = os.path.basename(fileName)[:6]
df['heure'] = pd.to_datetime(day + ' ' + df.time)
df['heureShift'] = df.heure.shift(1)
df['delay'] = df.heure - df.heureShift
df.delay = df.delay.apply(lambda x : x.seconds//60).replace(np.nan, 0)
#df.set_index('delay', inplace=True)


#%% 
plt.close('all')

def plotEvol(key):
    fig = plt.figure()
    fig.suptitle(key)
    ax = fig.add_subplot(111)
    ax.plot(df[key], '-o')
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return ax

#for key in df.columns:
for key in ['ph', 'po2', 'pco2']:
    ax = plotEvol(key)

#%% display the evolution of the blood gases iono, ....
    
plt.close('all')
def plotEvolO2Co2(df):
    fig = plt.figure(figsize=(8, 4))
    fig.suptitle('pO2 pco2')
    ax = fig.add_subplot(111)
    axT = ax.twinx()
    ax.plot(df.po2, '-or', alpha=0.8)
    ax.set_ylabel('paO2', color='r', alpha=0.8)
    axT.plot(df.pco2, '-ob', alpha=0.8)
    axT.set_ylabel('PaCO2', color='b', alpha=0.8)
    ax.spines["top"].set_visible(False)
    axT.spines["top"].set_visible(False)
    return fig

def plotAcidoBas(df):
    fig = plt.figure(figsize=(8, 4))
    fig.suptitle('acidoBasique')
    ax1 = fig.add_subplot(211)
    ax1.plot(df.ph, '-ok', alpha=0.5, label='ph')
    ax1.legend()
    ax2 = fig.add_subplot(212)
    ax2.plot(df.pco2, '-ob', label='pco2')
    ax2.set_ylabel('pco2', color='b', alpha=0.6)
    ax3 = ax2.twinx()
    ax3.plot(df.hco3, '-og')
    ax3.set_ylabel('hco3', color='g', alpha=0.6)
    
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax3.spines["top"].set_visible(False)
    fig.tight_layout()
    return fig
    

def plotMetabo(df):
    fig = plt.figure(figsize=(8, 4))
    fig.suptitle('métabo')
    ax = fig.add_subplot(111)
    ax.plot(df.hco3, '-og')
    ax.set_ylabel('hco3', color='g')
    axT = ax.twinx()
    axT.plot(df.angap, '-oc')
    axT.set_ylabel('angap', color='c')
    ax.spines["top"].set_visible(False)
    axT.spines["top"].set_visible(False)
    fig.tight_layout()

def plotIono(df):
    fig = plt.figure(figsize=(8, 4))
    fig.suptitle('iono')
    ax=fig.add_subplot(211)
    ax.plot(df.na, '-or', alpha=0.6)
    lims = ax.get_xlim()
#    ax.hlines(135, lims[0], lims[1], colors='r', alpha=0.5, linestyles='dashed')
#    ax.hlines(145, lims[0], lims[1], colors='r', alpha=0.5, linestyles='dashed')
    ax.set_ylabel('Na', color='r')
    axT = ax.twinx()
    axT.plot(df.cl, '-ob', alpha=0.6)
    axT.set_ylabel('Cl', color='b')
    lims = axT.get_xlim()
#    axT.hlines(110, lims[0], lims[1], colors='b', alpha=0.5, linestyles='dashed')
#    axT.hlines(95, lims[0], lims[1], colors='b', alpha=0.5, linestyles='dashed')
    
    ax2 = fig.add_subplot(212)
    ax2.plot(df.k, '-om', alpha=0.4)
    ax2.set_ylabel('K+', color='m', alpha=0.4)
    ax2T = ax2.twinx()
    ax2T.plot(df.ph, '-ok', alpha=0.4)
    ax2T.set_ylabel('pH', color='k', alpha=0.4)
    
    for ax in [ax, axT, ax2, ax2T]:
        ax.spines['top'].set_visible(False)
    
    fig.tight_layout() 

def plotHb(df):
    fig = plt.figure(figsize=(8,4))
    fig.suptitle('Hb')
    ax = fig.add_subplot(111)
    ax.plot(df.hb, '-or', alpha=0.6)
    ax.set_ylabel('Hb', color='r', alpha=0.6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()


    
plotEvolO2Co2(df)
plotAcidoBas(df)
plotMetabo(df)
plotIono(df)
plotHb(df)