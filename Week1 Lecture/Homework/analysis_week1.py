"""Week 1 - the frontier of Wikipedia's Marvel universe.

Everything the post claims is computed here. Figures go to the site's assets/img/,
numbers go to stdout. Both paths are found by walking up from this file, so it does not
matter which directory you run it from.

    python analysis_week1.py            # snapshot only (uses the API cache if present)
    python analysis_week1.py --wiki     # also fetches from the Wikipedia API
    python analysis_week1.py --json     # plus dump every number to week1_numbers.json

The API results are cached in Data/wiki_cache.json, so the second form only has to
run once.
"""

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))


def _find(*candidates):
    """Walk up from this file looking for one of these relative paths.

    The script lives in Week1 Lecture/Homework/ and writes into the site's assets/img/,
    two levels up, so it works from wherever it is invoked.
    """
    here = HERE
    for _ in range(5):
        for rel in candidates:
            path = os.path.join(here, *rel.split("/"))
            if os.path.isdir(path):
                return path
        here = os.path.dirname(here)
    return os.path.join(HERE, *candidates[0].split("/"))


DATA = _find("Data", "data")
IMG = _find("assets/img")
os.makedirs(IMG, exist_ok=True)

# --- Palette ---------------------------------------------------------------
# The site's own tokens (assets/css/site.css) converted to hex, then nudged until
# the categorical trio clears the lightness / chroma / colour-blind separation
# checks against the dark surface the post is read on.
INK    = "#fcf3f0"     # --text
MUTED  = "#b09893"     # --muted
GRID   = "#5a4441"
PANEL  = "#1d0c0b"     # --bg-panel, used as the mark outline
PAGE   = "#0c0403"     # --bg: baked into every PNG so the figure is never transparent
C_MAIN = "#e0523f"     # the giant component  (red)
C_RIM  = "#3d92d6"     # the rim: isolates and pendants  (blue)
C_ISL  = "#b78a1c"     # the island  (gold)

plt.rcParams.update({
    # Opaque, in the page's own background colour: seamless inside the post, and still
    # readable if the PNG is opened on its own (a transparent export goes checkerboard
    # in an image viewer and white-on-white on GitHub).
    "figure.facecolor": PAGE, "axes.facecolor": PAGE, "savefig.facecolor": PAGE,
    "font.family": "DejaVu Sans", "font.size": 10,
    "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": GRID, "axes.linewidth": 0.8,
    "grid.color": GRID, "grid.alpha": 0.35, "grid.linewidth": 0.6,
    "legend.frameon": False, "figure.dpi": 160,
})
HALO = [pe.withStroke(linewidth=2.6, foreground=PANEL)]


def despine(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def save(fig, name):
    path = os.path.join(IMG, name)
    fig.savefig(path, bbox_inches="tight", facecolor=PAGE)
    plt.close(fig)
    print("  wrote " + os.path.relpath(path, os.path.dirname(IMG)))


# --- 1. The graph ----------------------------------------------------------
# Roster first, edges second. Build from the edge list alone and the 17
# characters with no link in either direction disappear without a warning.

nodes = pd.read_csv(os.path.join(DATA, "week1_nodes.tsv"), sep="\t", comment="#")
edges = pd.read_csv(os.path.join(DATA, "week1_edges.tsv"), sep="\t",
                    comment="#", names=["source", "target"])

G = nx.DiGraph()
G.add_nodes_from(nodes.node_id)
G.add_edges_from(edges.itertuples(index=False, name=None))

NAME = dict(zip(nodes.node_id, nodes.name))
DESC = dict(zip(nodes.node_id, nodes.description))
ROSTER = set(nodes.node_id)


def short(n):
    return NAME.get(n, n).split(" (")[0]


U = G.to_undirected()
comps = sorted(nx.connected_components(U), key=len, reverse=True)
giant, island = comps[0], sorted(comps[1], key=lambda n: NAME[n])
isolates = sorted((n for n in G if G.degree(n) == 0), key=lambda n: NAME[n])
pendants = sorted((n for n in giant if U.degree(n) == 1), key=lambda n: NAME[n])

deg = dict(U.degree())
deg_in = dict(G.in_degree())
deg_out = dict(G.out_degree())
order = list(G.nodes())

# How each pendant is attached. Three cases, not two: it reaches in, it is reached
# for, or the single tie is reciprocal.
def pendant_kind(n):
    nb = list(U.neighbors(n))[0]
    there, back = G.has_edge(n, nb), G.has_edge(nb, n)
    return "both" if there and back else ("out" if there else "in")


pendant_out = [n for n in pendants if pendant_kind(n) == "out"]
pendant_in = [n for n in pendants if pendant_kind(n) == "in"]
pendant_both = [n for n in pendants if pendant_kind(n) == "both"]

STATS = {
    "n": G.number_of_nodes(),
    "m": G.number_of_edges(),
    "density": nx.density(G),
    "pairs": U.number_of_edges(),
    "reciprocal_pairs": G.number_of_edges() - U.number_of_edges(),
    "mean_in": G.number_of_edges() / G.number_of_nodes(),
    "density_u": nx.density(U),
    "mean_degree_u": 2 * U.number_of_edges() / U.number_of_nodes(),
    "components": len(comps),
    "giant": len(giant),
    "island": len(island),
    "island_edges": G.subgraph(island).number_of_edges(),
    "isolates": len(isolates),
    "pendants": len(pendants),
    "pendants_outward": len(pendant_out),
    "pendants_inward": len(pendant_in),
    "pendants_both": len(pendant_both),
    "reciprocity": nx.reciprocity(G),
    "rim_le_3": sum(1 for n in G if deg[n] <= 3),
}


def report():
    # Both conventions, spelled out. "Average degree" and "density" mean different
    # numbers depending on whether you keep the direction or collapse the 350
    # reciprocal pairs first, and quoting one without saying which is how two people
    # analysing the same file end up publishing different constants.
    print("n=%(n)d  directed edges=%(m)d  undirected pairs=%(pairs)d "
          "(%(reciprocal_pairs)d of them reciprocal)" % STATS)
    print("directed:   density=%(density).4f  mean in-degree=%(mean_in).2f" % STATS)
    print("undirected: density=%(density_u).4f  <k>=%(mean_degree_u).2f" % STATS)
    print("components=%(components)d  giant=%(giant)d  island=%(island)d "
          "(%(island_edges)d internal links)  isolates=%(isolates)d" % STATS)
    print("pendants=%(pendants)d: %(pendants_outward)d only link out, "
          "%(pendants_inward)d is only linked to, %(pendants_both)d go both ways" % STATS)
    print("reciprocity=%(reciprocity).3f   degree<=3: %(rim_le_3)d characters" % STATS)


# --- 2. Figure 1 - the map -------------------------------------------------
# The hero image: continent, island, castaways, and the threads the rim throws
# at the centre.

def fig_map():
    fig, ax = plt.subplots(figsize=(9.8, 6.8))

    def unit(p):
        xy = np.array(list(p.values()))
        span = xy.max(0) - xy.min(0)
        span[span == 0] = 1
        return {n: 2 * (v - (xy.max(0) + xy.min(0)) / 2) / span.max() for n, v in p.items()}

    # Lay out the giant component on its own; a whole-graph layout just flings the
    # unconnected pieces into the corners, which says nothing.
    pos = unit(nx.spring_layout(U.subgraph(giant), seed=11, iterations=600))
    pos = {n: v * np.array([1.0, 0.92]) for n, v in pos.items()}

    isl = unit(nx.spring_layout(U.subgraph(island), seed=3, iterations=400))
    for n, v in isl.items():
        pos[n] = v * 0.22 + np.array([1.80, 0.46])
    for i, n in enumerate(isolates):
        pos[n] = np.array([1.62 + (i % 3) * 0.18, -0.34 - (i // 3) * 0.16])

    pend = set(pendants)
    sizes, colors, edgecols, widths = [], [], [], []
    for n in G.nodes():
        sizes.append(10 + 30 * np.sqrt(deg[n]))
        if n in island:
            colors.append(C_ISL); edgecols.append(PANEL); widths.append(0.5)
        elif n in isolates:
            colors.append(C_RIM); edgecols.append(PANEL); widths.append(0.5)
        elif n in pend:
            colors.append(C_RIM); edgecols.append(INK); widths.append(1.0)
        else:
            colors.append(C_MAIN); edgecols.append(PANEL); widths.append(0.5)

    # Draw the pendants' single threads on top, in the rim colour.
    pend_edges = [(u, v) for u, v in G.edges() if u in pend or v in pend]
    rest_edges = [(u, v) for u, v in G.edges() if u not in pend and v not in pend]
    nx.draw_networkx_edges(G, pos, edgelist=rest_edges, ax=ax, edge_color="#e09a8e",
                           alpha=0.18, width=0.5, arrows=False)
    nx.draw_networkx_edges(G, pos, edgelist=pend_edges, ax=ax, edge_color=C_RIM,
                           alpha=0.75, width=1.0, arrows=False)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=sizes, node_color=colors,
                           alpha=0.92, edgecolors=edgecols, linewidths=widths)

    for n, (tx, ty) in {"Spider-Man": (-1.05, 0.66), "Hulk": (-1.15, 0.24),
                        "Wolverine_(character)": (-0.98, -1.02),
                        "Doctor_Strange": (0.60, -1.06)}.items():
        ax.annotate(short(n), xy=pos[n], xytext=(tx, ty), ha="left", va="center",
                    color=INK, fontsize=9, zorder=6, path_effects=HALO,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7, alpha=0.7,
                                    shrinkA=2, shrinkB=6,
                                    connectionstyle="arc3,rad=0.12"))

    ax.text(1.80, 0.98, "Strikeforce: Morituri", ha="center", color=C_ISL,
            fontsize=10, fontweight="bold")
    ax.text(1.80, 0.88, "9 characters, %d links,\nnone of them off the island"
            % STATS["island_edges"], ha="center", va="top", color=C_ISL, fontsize=8.5)
    ax.text(1.80, -0.16, "17 castaways", ha="center", color=C_RIM, fontsize=10,
            fontweight="bold")
    ax.text(1.80, -0.24, "no link in or out", ha="center", va="top", color=MUTED,
            fontsize=8.5)
    ax.text(-1.15, 1.02, "18 pendants", color=C_RIM, fontsize=10, fontweight="bold")
    ax.text(-1.15, 0.94, "held by one single link\n(blue threads)", va="top",
            color=MUTED, fontsize=8.5)
    ax.text(-1.15, -1.24, "giant component  .  277 of the 303 characters",
            ha="left", color=MUTED, fontsize=9)

    # The two castaways the post argues about, called out by name.
    for nid in ("Baymax", "Miracleman_(character)"):
        ax.annotate(short(nid), xy=pos[nid], xytext=(pos[nid][0], pos[nid][1] - 0.062),
                    ha="center", va="center", color=INK, fontsize=8.5, zorder=7,
                    path_effects=HALO)

    ax.set_title("The frontier: one continent, one island, seventeen castaways",
                 color=INK, loc="left", fontsize=12.5, pad=12)
    ax.set_axis_off()
    ax.set_xlim(-1.20, 2.32)
    ax.set_ylim(-1.34, 1.16)
    fig.tight_layout()
    save(fig, "week1_frontier_map.png")


# --- 3. Figure 2 - degree distributions ------------------------------------
# The +1 shift is not cosmetic: without it the 17 castaways fall off the log axis,
# which is precisely the population this post is about.

def fig_degrees():
    kin = np.array([deg_in[n] for n in order])
    kout = np.array([deg_out[n] for n in order])
    ktot = np.array([deg[n] for n in order])

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9))

    ax = axes[0]
    ax.hist(ktot, bins=np.arange(0, 62, 2), histtype="stepfilled", color=C_MAIN,
            alpha=0.16, zorder=2)
    ax.hist(ktot, bins=np.arange(0, 62, 2), histtype="step", color=C_MAIN, lw=2,
            zorder=3)
    ax.axvspan(-0.5, 3.5, color=C_RIM, alpha=0.13, zorder=1)
    ax.set_xlabel("total degree $k$   (linear axes, tail cropped at 60)")
    ax.set_ylabel("characters")
    ax.set_title("A third of the map is rim", color=INK, loc="left", fontsize=11, pad=8)
    ax.grid(axis="y", zorder=0)
    ax.annotate("%d characters with $k \\leq 3$\n(%.0f%% of the roster)"
                % (STATS["rim_le_3"], 100 * STATS["rim_le_3"] / STATS["n"]),
                xy=(4, 30), xytext=(17, 46), color=C_RIM, fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color=C_RIM, lw=0.8,
                                connectionstyle="arc3,rad=0.2"))
    ax.annotate("17 of them at $k = 0$:\nthe castaways", xy=(0.6, 34),
                xytext=(6.5, 20), color=C_RIM, fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color=C_RIM, lw=0.8,
                                connectionstyle="arc3,rad=-0.25"))
    despine(ax)

    ax = axes[1]
    for k, c, lab in ((kin, C_MAIN, "in-degree"), (kout, C_ISL, "out-degree")):
        vals, cnt = np.unique(k + 1, return_counts=True)
        ax.plot(vals, cnt / cnt.sum(), "o", color=c, ms=5.5, alpha=0.85,
                markeredgecolor=PANEL, markeredgewidth=0.6, label=lab)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1.6e-3, 0.45)
    ax.set_xlabel("$k+1$   (the $+1$ is what keeps the castaways on a log axis)")
    ax.set_ylabel("$P(k)$")
    ax.set_title("Two different tails", color=INK, loc="left", fontsize=11, pad=8)
    ax.grid(which="major")
    ax.legend(labelcolor=INK, loc="lower left")
    ax.annotate("in-degree runs to 106\n(Spider-Man)", xy=(107, 1 / 303),
                xytext=(15, 0.055), color=C_MAIN, fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color=C_MAIN, lw=0.8,
                                connectionstyle="arc3,rad=-0.2"))
    ax.annotate("out-degree stops at 28", xy=(29, 1 / 303), xytext=(4.5, 0.0075),
                color=C_ISL, fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color=C_ISL, lw=0.8,
                                connectionstyle="arc3,rad=0.25"))
    despine(ax)

    fig.tight_layout()
    save(fig, "week1_degree_distributions.png")


# --- 4. Figure 3 - which way the links point -------------------------------
# Polarity = (in - out) / (in + out). -1 means a character only links out,
# +1 means it is only linked to. Plotted against degree it generalises what the
# 18 pendants show one at a time.

def polarity_frame():
    rows = []
    for n in order:
        tot = deg_in[n] + deg_out[n]
        if tot == 0:
            continue
        rows.append((n, deg[n], (deg_in[n] - deg_out[n]) / tot, n in set(pendants)))
    return pd.DataFrame(rows, columns=["node", "k", "polarity", "pendant"])


def fig_polarity():
    df = polarity_frame()
    fig, ax = plt.subplots(figsize=(8.0, 5.0))

    ax.axhline(0, color=GRID, lw=1, ls="--", zorder=1)
    ax.text(1.35, 0.04, "links out and is linked to equally often", color=MUTED,
            fontsize=8.5, ha="left", va="bottom")

    rest = df[~df.pendant]
    ax.scatter(rest.k, rest.polarity, s=26, color=MUTED, alpha=0.35, edgecolor="none",
               zorder=3, label="the other 268 characters")
    pend = df[df.pendant]
    ax.scatter(pend.k, pend.polarity, s=54, color=C_RIM, edgecolor=PANEL, linewidth=0.7,
               zorder=5, label="the 18 pendants (one link each)")

    # All 18 pendants sit on x = 1, so they stack; say how many are on each pile.
    for pol, va, dy in ((-1.0, "bottom", 6), (1.0, "top", -6)):
        count = int((pend.polarity == pol).sum())
        if count:
            ax.annotate("%d %s\n%s" % (count, "pendant" if count == 1 else "pendants",
                                       "reaching in" if pol < 0 else "reached for"),
                        xy=(1, pol), textcoords="offset points", xytext=(12, dy),
                        va=va, color=C_RIM, fontsize=8.5, zorder=7, path_effects=HALO)

    # Median polarity in degree bins - the trend, not the noise.
    bins = [1, 2, 3, 5, 8, 13, 21, 34, 55, 130]
    mids, meds = [], []
    for lo, hi in zip(bins[:-1], bins[1:]):
        sel = df[(df.k >= lo) & (df.k < hi)]
        if len(sel) >= 5:
            mids.append(np.sqrt(lo * hi))
            meds.append(sel.polarity.median())
    ax.plot(mids, meds, color=C_MAIN, lw=2.4, zorder=6, label="median, by degree")

    for n, dy in (("Spider-Man", 10), ("Hulk", -16), ("Betsy_Braddock", 10)):
        row = df[df.node == n].iloc[0]
        ax.scatter([row.k], [row.polarity], s=52, color=C_MAIN, edgecolor=PANEL,
                   linewidth=0.7, zorder=7)
        ax.annotate(short(n), (row.k, row.polarity), textcoords="offset points",
                    xytext=(0, dy), ha="center", color=INK, fontsize=8.5, zorder=8,
                    path_effects=HALO)

    ax.set_xscale("log")
    ax.set_xlabel("total degree $k$  (log axis)")
    ax.set_ylabel("polarity   (in $-$ out) / (in $+$ out)")
    ax.set_title("The rim reaches in; the centre does not reach back",
                 color=INK, loc="left", fontsize=12, pad=10)
    ax.set_ylim(-1.25, 1.25)
    ax.grid(axis="y")
    ax.legend(labelcolor=INK, loc="upper center", bbox_to_anchor=(0.5, -0.16),
              ncol=3, fontsize=8.5)
    ax.text(1.35, -1.18, "only links out", color=MUTED, fontsize=8.5)
    ax.text(1.35, 1.12, "only linked to", color=MUTED, fontsize=8.5)
    despine(ax)
    fig.tight_layout()
    save(fig, "week1_polarity.png")


# --- 5. Figure 4 - is it just article length? ------------------------------
# The obvious rival explanation: the castaways are stubs nobody finished writing.
# prop=info gives the byte size of every article, so this is testable.

def length_frame():
    import wiki
    sizes = wiki.article_bytes(list(nodes.node_id))
    rows = []
    for n in order:
        if sizes.get(n):
            group = ("castaway" if n in isolates else
                     "island" if n in island else "connected")
            rows.append((n, group, deg[n], sizes[n]))
    return pd.DataFrame(rows, columns=["node", "group", "k", "bytes"])


def fig_length(df):
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    groups = [("connected", C_MAIN, "in the giant component"),
              ("island", C_ISL, "the Morituri island"),
              ("castaway", C_RIM, "the 17 castaways")]
    rng = np.random.default_rng(4)

    for i, (key, colour, label) in enumerate(groups):
        sel = df[df.group == key]
        y = i + rng.uniform(-0.16, 0.16, len(sel))
        ax.scatter(sel["bytes"] / 1000, y, s=30, color=colour, alpha=0.5,
                   edgecolor="none", zorder=3, label=label)
        med = sel["bytes"].median() / 1000
        ax.plot([med, med], [i - 0.3, i + 0.3], color=INK, lw=2.4, zorder=5)
        ax.annotate("median %.1f kB" % med, (med, i + 0.34), color=INK, fontsize=8.5,
                    ha="center", zorder=6, path_effects=HALO)

    big = df[df.group == "castaway"].sort_values("bytes").iloc[-1]
    ax.annotate("%s: %.0f kB and not one link" % (short(big.node), big["bytes"] / 1000),
                xy=(big["bytes"] / 1000, 2), xytext=(20, 1.35), color=C_RIM,
                fontsize=8.5, path_effects=HALO,
                arrowprops=dict(arrowstyle="->", color=C_RIM, lw=0.8,
                                connectionstyle="arc3,rad=0.25"))

    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([g[2] for g in groups], color=INK)
    ax.set_xscale("log")
    ax.set_xlabel("article size (kB of wiki-source, log axis)")
    ax.set_title("Short articles, yes - but that is not the whole story",
                 color=INK, loc="left", fontsize=12, pad=10)
    ax.grid(axis="x", which="major")
    ax.set_ylim(-0.6, 2.7)
    despine(ax)
    fig.tight_layout()
    save(fig, "week1_article_size.png")


def length_stats(df):
    cast = df[df.group == "castaway"]["bytes"]
    rest = df[df.group != "castaway"]["bytes"]
    print("\narticle size (kB): castaways median %.1f, everyone else %.1f"
          % (cast.median() / 1000, rest.median() / 1000))
    print("  overlap: %d of %d castaways are bigger than the median connected article"
          % ((cast > rest.median()).sum(), len(cast)))
    print("  spearman(size, degree) over the whole roster: %.3f"
          % df["bytes"].corr(df.k, method="spearman"))
    return {
        "castaway_median_kb": round(cast.median() / 1000, 1),
        "connected_median_kb": round(rest.median() / 1000, 1),
        "spearman_size_degree": round(df["bytes"].corr(df.k, method="spearman"), 3),
        "castaways_above_connected_median": int((cast > rest.median()).sum()),
    }


# --- 6. The stretch: check the snapshot against live Wikipedia --------------
# The castaways' isolation is a claim about harvested data. Re-harvest it.

def verify(sample):
    import wiki
    rows = []
    for nid in sample:
        raw, titles = wiki.outlinks(nid)
        found = set(titles) & ROSTER - {nid}
        snap = set(edges[edges.source == nid].target)
        rows.append((short(nid), len(raw), len(found), len(snap), len(found & snap)))
    df = pd.DataFrame(rows, columns=["article", "[[links]] in source",
                                     "inside the roster", "in the snapshot", "agreeing"])
    print("\nsnapshot vs. live wiki-source\n" + df.to_string(index=False))
    return df


def island_looks_outward(sample=None):
    """Do the Morituri articles link anywhere at all, or are they just stubs?

    Splits their links three ways: everything they link to, the peers inside their
    own island, and anyone in the roster outside it. The third column is the point.
    """
    import wiki
    sample = sample or island
    rows = []
    for nid in sample:
        raw, titles = wiki.outlinks(nid)
        in_roster = set(titles) & ROSTER - {nid}
        rows.append((short(nid), len(raw), len(in_roster & set(island)),
                     len(in_roster - set(island))))
    df = pd.DataFrame(rows, columns=["article", "[[links]] in source",
                                     "to island peers", "to anyone else in the roster"])
    print("\nthe island's articles do link out - just never off the island\n"
          + df.to_string(index=False))
    return df


def size_residuals(df):
    """The castaways that article length cannot explain away."""
    big = df[(df.group == "castaway") & (df["bytes"] >= 20000)]
    band = df[(df.group == "connected") & (df["bytes"] >= 20000) & (df["bytes"] <= 70000)]
    print("\ncastaways too big to be dismissed as stubs:")
    for _, r in big.sort_values("bytes", ascending=False).iterrows():
        print("  %-24s %5.0f kB, degree 0" % (short(r.node), r["bytes"] / 1000))
    print("  connected articles of 20-70 kB: median degree %.0f (n=%d)"
          % (band.k.median(), len(band)))
    return {"band_median_degree": int(band.k.median()), "band_n": int(len(band)),
            "big_castaways": [short(r.node) for _, r in big.iterrows()]}


# --- 7. Tables the post uses -----------------------------------------------

def tables():
    print("\nthe 17 castaways")
    for n in isolates:
        print("  %-30s %s" % (NAME[n], str(DESC[n])[:96]))
    print("\nthe island")
    for n in island:
        print("  %-28s in=%d out=%d" % (NAME[n], deg_in[n], deg_out[n]))
    print("\nthe pendants and what they hold on to")
    for n in pendants:
        nb = list(U.neighbors(n))[0]
        way = "is linked to by" if G.has_edge(nb, n) else "links out to"
        print("  %-28s %-16s %s" % (NAME[n], way, NAME[nb]))


if __name__ == "__main__":
    report()
    print("\nfigures:")
    fig_map()
    fig_degrees()
    fig_polarity()

    numbers = dict(STATS)
    if "--wiki" in sys.argv or os.path.exists(os.path.join(DATA, "wiki_cache.json")):
        sizes = length_frame()
        fig_length(sizes)
        numbers.update(length_stats(sizes))
        numbers.update(size_residuals(sizes))
        verify(["Miracleman_(character)", "Baymax", "Toxyn", "Spider-Man"])
        island_looks_outward()
    tables()

    if "--json" in sys.argv:      # opt-in, so a plain run leaves no build output behind
        out = os.path.join(HERE, "week1_numbers.json")
        with open(out, "w") as fh:
            json.dump(numbers, fh, indent=1, sort_keys=True)
        print("\nnumbers used by the post -> " + os.path.basename(out))
