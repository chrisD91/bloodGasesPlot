# -*- coding: utf-8 -*-


import matplotlib.pyplot as plt

from matplotlib import rc

# rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
rc("font", **{"family": "serif", "serif": ["Palatino"]})
rc("font", size=14)
rc("text", usetex=True)

# horse
usual = dict(
    o2=[80, 112],
    co2=[36, 46],
    ph=[3.34, 7.48],
    hco3=[22, 29],
    angap=[5, 16],
    na=[136, 142],
    cl=[98, 104],
    k=[2.2, 4],
)


# ca
# mg
# phosphates
# protein


#%%

plt.close("all")


def plot_aniongap(**kwargs):
    """
    plot the normal anionGap values
    input  na (140) k (3.5), cl = 105, hco3 = 24,

    Returns
    -------
    fig : matplotlib figure

    """
    iono_std = dict(na=140, k=3.5, cl=105, hco3=24, albu=40, phosphore=1)
    vals = iono_std.copy()
    vals.update(kwargs)

    categories = ["cations", "anions"]

    # [na, indosés(mg, ca, k)]
    cations = [140, 5, 25]
    cations = [vals["na"], vals["k"], 25]
    print(cations)

    # [cl, hco3, albumine, phosphate, indosés (Xa, lactates)]
    anions = [105, 25]
    anions = [vals["cl"], vals["hco3"]]
    print(anions)

    fig = plt.figure(figsize=(6, 8))
    ax = fig.add_subplot(111)
    base = sum(cations)
    colors = ["tab:red", "tab:purple", "k"]
    fills = [True, True, False]
    for i, v in enumerate(cations):
        ax.bar(
            categories[0],
            v,
            bottom=base - v,
            ec="k",
            color=colors[i],
            fill=fills[i],
            linewidth=3,
            alpha=0.3,
        )
        base -= v
    base = sum(cations)
    colors = ["tab:green", "tab:blue", "k"]
    fills = [True, True, False]
    for i, v in enumerate(anions):
        ax.bar(
            categories[1],
            v,
            bottom=base - v,
            ec="k",
            color=colors[i],
            fill=fills[i],
            linewidth=3,
            alpha=0.3,
        )
        base -= v
    ax.bar(categories[1], base, bottom=0, ec="k", fill=False)

    yval = sum(cations) - anions[0] - anions[1]

    ax.hlines(cations[2], -0.5, 0.6, "k", linewidth=3, linestyles=":")
    ax.hlines(yval, 0.4, 1.5, "k", linewidth=3, linestyles=":")

    agap = vals["na"] + vals["k"] - vals["cl"] - vals["hco3"]
    ax.annotate(
        "anion gap {}".format(agap),
        xy=(0.5, cations[1] + (yval - cations[1]) / 2),
        xytext=(0.5, -10),
        arrowprops=dict(arrowstyle="fancy"),
        ha="center",
        bbox=dict(boxstyle="round,pad=0.2", fc="yellow", alpha=1, ec="k"),
    )

    ax.set_ylabel("mmol/L")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.text(0, 140, r"$Na^+$", ha="center", va="center", color="k")
    y = sum(cations) - cations[0] - 0.5 * cations[1]
    st = r"$K^+$"
    ax.text(0, y, st, color="k", ha="center", va="center")
    y = sum(cations) - cations[0] - cations[1] - 0.5 * cations[2]
    st = r"$Ca^{2+} \ Mg^{2+}$"
    ax.text(0, y, st, color="k", ha="center", va="center")
    ax.text(
        1,
        140,
        r"$Cl^-$",
        color="k",
        ha="center",
        va="center",
    )

    y = sum(cations) - anions[0] - 0.5 * anions[1]
    ax.text(1, y, r"$HCO_3-$", color="k", ha="center", va="center")

    y = (sum(cations) - anions[0] - anions[1]) / 3
    step = y / 2
    st = r"$xA^-$,  lactates"
    ax.text(1, y - step, st, ha="center", va="center")
    st = "phosphates"
    ax.text(1, 2 * y - step, st, ha="center", va="center")
    st = "albumine"
    ax.text(1, 3 * y - step, st, ha="center", va="center")

    st = r"NB    pH = f(SID,   $PaCO_2$,   $\sum$ acides faibles)"
    st = r"$anion\ gap = Na^+ K^+ - (Cl^- + HCO_3^-)$     (~12 ± 2)"
    fig.suptitle(st)

    fig.text(
        0.01,
        0.01,
        "adapté de Quintard 2007",
        ha="left",
        va="bottom",
        alpha=0.4,
        size=12,
    )
    fig.text(0.99, 0.01, "cDesbois", ha="right", va="bottom", alpha=0.4, size=12)

    return fig


fig = plot_aniongap()
