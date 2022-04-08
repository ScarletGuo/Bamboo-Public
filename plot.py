import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional

# "pdf", "eps", "png", etc
IMAGE_TYPE = "pdf"

# based on: https://colorbrewer2.org/#type=qualitative&scheme=Set3&n=5
# this color map ensure the curves are still readable in grayscale
color_map = {
    "NO_WAIT": "#8dd3c7",
    "WAIT_DIE": "#80b1d3",
    "WOUND_WAIT": "#bebada",
    "SILO": "#fdaa48",
    "SILO_PRIO": "#fb8072",
    # log scale plot
    "SILO_PRIO:High": "#fb8072",
    "SILO_PRIO:Low": "#fb8072",
    "SILO_PRIO_FIXED": "#bebada",
    "SILO_PRIO_FIXED:High": "#bebada",
    "SILO_PRIO_FIXED:Low": "#bebada",
}

# linestyle and marker are unused if making bar graph instead of plot
linestyle_map = {
    "NO_WAIT": "-",
    "WAIT_DIE": "-",
    "WOUND_WAIT": "-",
    "SILO": "-",
    "SILO_PRIO": "-",
    # log scale plot:
    "SILO_PRIO:High": "-",
    "SILO_PRIO:Low": "--",
    "SILO_PRIO_FIXED:High": "-",
    "SILO_PRIO_FIXED:Low": "--",
}

marker_map = {
    "NO_WAIT": "^",
    "WAIT_DIE": "s",
    "WOUND_WAIT": "d",
    "SILO": "x",
    "SILO_PRIO": "o",
}

label_map = {
    "NO_WAIT": "NO_WAIT",
    "WAIT_DIE": "WAIT_DIE",
    "WOUND_WAIT": "WOUND_WAIT",
    "SILO": "SILO",
    "SILO_PRIO": "SILO_PRIO",
    "SILO_PRIO_FIXED": "SILO_PRIO_FIXED",
    "SILO_PRIO:High": "SILO_PRIO:High",
    "SILO_PRIO:Low": "SILO_PRIO:Low",
    "SILO_PRIO_FIXED:High": "SILO_PRIO_FIXED:High",
    "SILO_PRIO_FIXED:Low": "SILO_PRIO_FIXED:Low",
}

marker_size = 4

FIG_SIZE = (5, 2.5)


def set_fig(fig, fig_size=FIG_SIZE):
    # handle all figure parameters tuning
    fig.set_tight_layout({"pad": 0.01, "w_pad": 0.5, "h_pad": 0})
    fig.set_size_inches(*fig_size)


def get_subplots_UD(fig_size=FIG_SIZE):
    fig, axes = plt.subplots(nrows=2, ncols=1)
    set_fig(fig, fig_size=fig_size)
    return fig, axes


def get_subplots_LR(fig_size=FIG_SIZE):
    fig, axes = plt.subplots(nrows=1, ncols=2)
    set_fig(fig, fig_size=fig_size)
    return fig, axes


def get_subplots_2L1R(fig_size=FIG_SIZE):
    fig = plt.figure()
    ax_l = fig.add_subplot(1, 3, (1, 2))
    ax_r = fig.add_subplot(1, 3, 3)
    set_fig(fig, fig_size=fig_size)
    return fig, (ax_l, ax_r)


def make_subplot(df: pd.DataFrame, ax, x_col: str, y_col: str, z_col: str,
                 x_range: List[int], z_range: List, filters: Dict):
    filter_df = df
    for fk, fv in filters.items():
        filter_df = filter_df[(filter_df[fk] == fv)]

    # each z corresponds to a legend
    for z_val in z_range:
        z_df = filter_df[(filter_df[z_col] == z_val)]
        y_data = []
        for x_val in x_range:
            d = z_df[(z_df[x_col] == x_val)]
            if d.shape[0] != 1:
                raise ValueError(
                    f"Unexpected data: ({x_col}={x_val},{z_col}={z_val}): shape {d.shape}")
            y_data.append(d.head(1)[y_col])
        ax.plot(x_range, y_data,
                color=color_map[z_val],
                marker=marker_map[z_val],
                markersize=marker_size,
                label=label_map[z_val])


def make_tail_latency_subplot(df: pd.DataFrame, ax, z_col: str,
                              prio_range: Optional[Tuple[int, int]] = None):
    filtered_df = df
    if prio_range:
        prio_min, prio_max = prio_range
        filtered_df = df[(df['prio'] >= prio_min) & (df['prio'] <= prio_max)]
    latency = filtered_df['latency'].to_numpy()
    latency.sort()
    latency = latency / 1e6
    p = np.arange(len(latency)) / len(latency)

    ax.plot(latency, -np.log10(1 - p), color=color_map[z_col],
            linestyle=linestyle_map[z_col], label=label_map[z_col])


def plot_ycsb_thread_vs_throughput_tail(exper: str, tail_metric='p999', layout='LR'):
    assert layout in {"LR", "UD"}
    fig, (ax_tp, ax_tail) = get_subplots_LR() \
        if layout == 'LR' else get_subplots_UD()

    cc_algs = ["NO_WAIT", "WAIT_DIE", "WOUND_WAIT", "SILO", "SILO_PRIO"]
    thread_cnts = [1, 4, 8, 16, 24, 32, 40, 48, 56, 64]

    # plot throughput
    tp_df = pd.read_csv(f"results/{exper}/throughput.csv", header=0,
                        na_values="None", skipinitialspace=True)
    make_subplot(df=tp_df, ax=ax_tp, x_col='thread_cnt', y_col='throughput',
                 z_col='cc_alg', x_range=thread_cnts, z_range=cc_algs,
                 filters={"zipf_theta": 0.99})

    # plot tail latency
    tail_df = pd.read_csv(f"results/{exper}/tail.csv", header=0,
                          na_values="None", skipinitialspace=True)
    make_subplot(df=tail_df, ax=ax_tail, x_col='thread_cnt', y_col=tail_metric,
                 z_col='cc_alg', x_range=thread_cnts, z_range=cc_algs,
                 filters={"zipf_theta": 0.99, 'tag': 'all'})

    ax_tp.set_xlabel('Number of threads')
    ax_tail.set_xlabel('Number of threads')

    ax_tp.set_xticks([1, 8, 16, 32, 48, 64])
    ax_tail.set_xticks([1, 8, 16, 32, 48, 64])
    ax_tp.set_xlim(0)
    ax_tail.set_xlim(0)

    return fig, (ax_tp, ax_tail)


def plot_ycsb_zipf_vs_throughput_tail(exper: str, tail_metric='p999', layout='LR'):
    assert layout in {"LR", "UD"}
    fig, (ax_tp, ax_tail) = get_subplots_LR() \
        if layout == 'LR' else get_subplots_UD()

    cc_algs = ["NO_WAIT", "WAIT_DIE", "WOUND_WAIT", "SILO", "SILO_PRIO"]
    zipf_thetas = [0.9, 0.99, 1.1, 1.2, 1.3, 1.4, 1.5]

    # plot throughput
    tp_df = pd.read_csv(f"results/{exper}/throughput.csv", header=0,
                        na_values="None", skipinitialspace=True)
    make_subplot(df=tp_df, ax=ax_tp, x_col='zipf_theta', y_col='throughput',
                 z_col='cc_alg', x_range=zipf_thetas, z_range=cc_algs,
                 filters={"thread_cnt": 64})

    # plot tail latency
    tail_df = pd.read_csv(f"results/{exper}/tail.csv", header=0,
                          na_values="None", skipinitialspace=True)
    make_subplot(df=tail_df, ax=ax_tail, x_col='zipf_theta', y_col=tail_metric,
                 z_col='cc_alg', x_range=zipf_thetas, z_range=cc_algs,
                 filters={"thread_cnt": 64, 'tag': 'all'})

    zipf_ticks = zipf_thetas
    ax_tp.set_xticks(
        zipf_ticks, [f"{t:.1f}" if t != 0.99 else f"{t:.2f}" for t in zipf_ticks])
    ax_tail.set_xticks(
        zipf_ticks, [f"{t:.1f}" if t != 0.99 else f"{t:.2f}" for t in zipf_ticks])

    tp_ticks = list(range(0, 600001, 100000))
    ax_tp.set_yticks(
        tp_ticks, [f"{t/1e6}" if t > 0 else "0" for t in tp_ticks], rotation=90)
    ax_tp.set_ylim([0, 600000])

    tail_ticks = list(range(0, 16001, 4000))
    ax_tail.set_yticks(
        tail_ticks, [f"{t//1000}" if t > 0 else "0" for t in tail_ticks], rotation=90)
    ax_tail.set_ylim([0, 16000])

    ax_tp_zoom = ax_tp.inset_axes([0.45, 0.45, 0.5, 0.5])
    make_subplot(df=tp_df, ax=ax_tp_zoom, x_col='zipf_theta', y_col='throughput',
                 z_col='cc_alg', x_range=[1.2, 1.3, 1.4, 1.5], z_range=cc_algs,
                 filters={"thread_cnt": 64})
    tp_ticks_zoom = list(range(0, 160001, 80000))
    ax_tp_zoom.set_xticks([1.2, 1.3, 1.4, 1.5])
    ax_tp_zoom.set_yticks(
        tp_ticks_zoom, [f"{t/1e6}" if t > 0 else "0" for t in tp_ticks_zoom], rotation=90)
    ax_tp_zoom.set_ylim([0, 160000])

    ax_tp.set_ylabel('Throughput (Mtxn/s)')
    ax_tail.set_ylabel(f'Tail latency {tail_metric} (ms)')
    ax_tp.set_xlabel('Zipfian theta')
    ax_tail.set_xlabel('Zipfian theta')

    return fig, (ax_tp, ax_tail)


def plot_latency_logscale_throughput(exper: str, thread_cnt=64, zipf=0.99):
    fig, (ax_tail, ax_tp) = get_subplots_2L1R()

    # SILO
    cc_alg = "SILO"
    data_path = f"results/{exper}/YCSB-CC={cc_alg}-THD={thread_cnt}-ZIPF={zipf}/latency_dump.csv"
    df = pd.read_csv(data_path, header=0, names=['prio', 'latency'],
                     na_values="None", skipinitialspace=True)
    make_tail_latency_subplot(df, ax_tail, "SILO")

    # then SILO_PRIO_FIXED
    cc_alg = "SILO_PRIO_FIXED"
    data_path = f"results/{exper}/YCSB-CC={cc_alg}-THD={thread_cnt}-ZIPF={zipf}/latency_dump.csv"
    df = pd.read_csv(data_path, header=0, names=['prio', 'latency'],
                     na_values="None", skipinitialspace=True)
    make_tail_latency_subplot(df, ax_tail, f"{cc_alg}:High", [8, 15])
    make_tail_latency_subplot(df, ax_tail, f"{cc_alg}:Low", [0, 7])

    # finally, SILO_PRIO
    cc_alg = "SILO_PRIO"
    data_path = f"results/{exper}/YCSB-CC={cc_alg}-THD={thread_cnt}-ZIPF={zipf}/latency_dump.csv"
    df = pd.read_csv(data_path, header=0, names=['prio', 'latency'],
                     na_values="None", skipinitialspace=True)
    make_tail_latency_subplot(df, ax_tail, f"{cc_alg}:High", [8, 15])
    make_tail_latency_subplot(df, ax_tail, f"{cc_alg}:Low", [0, 7])

    ax_tail.grid(True, axis='y', linestyle='--', linewidth=0.1)

    ax_tail.set_xlim(0, 3)
    ax_tail.set_ylim(0, 4)

    ax_tail.set_yticks([0, 1, 2, 3, 4], ["0", "p90", "p99", "p999", "p9999"],
                       rotation=90)

    ax_tail.set_xlabel("Latency (ms)")
    ax_tail.set_ylabel(f"Tail percentage")

    # then draw bar-graph for throughput
    tp_df = pd.read_csv(f"results/{exper}/throughput.csv", header=0,
                        na_values="None", skipinitialspace=True)
    for i, cc_alg in enumerate(["SILO", "SILO_PRIO_FIXED", "SILO_PRIO"]):
        d = tp_df[(tp_df["cc_alg"] == cc_alg)]
        assert d.shape[0] == 1
        ax_tp.bar(i, d.head(1)["throughput"],
                  width=0.6, color=color_map[cc_alg], label=label_map[cc_alg])

    # ax_tp.set_xticks([0, 1, 2], ["SILO", "SILO_PRIO_FIXED", "SILO_PRIO"], rotation=45)
    plt.xticks([], [])
    tp_ticks = list(range(0, 600001, 100000))
    ax_tp.set_yticks(tp_ticks, [f"{t / 1e6}" for t in tp_ticks], rotation=90)
    ax_tp.set_ylim([0, 600000])

    ax_tp.set_xlabel('Algorithm')
    ax_tp.set_ylabel('Throughput (Mtxn/s)')

    return fig, (ax_tail, ax_tp)


def plot_tpcc_thread_vs_throughput_tail(exper: str, tail_metric='p999', layout='LR'):
    assert layout in {"LR", "UD"}
    fig, (ax_tp, ax_tail) = get_subplots_LR() \
        if layout == 'LR' else get_subplots_UD()

    cc_algs = ["NO_WAIT", "WAIT_DIE", "WOUND_WAIT", "SILO", "SILO_PRIO"]
    thread_cnts = [1, 4, 8, 16, 24, 32, 40, 48, 56, 64]

    # plot throughput
    tp_df = pd.read_csv(f"results/{exper}/throughput.csv", header=0,
                        na_values="None", skipinitialspace=True)
    make_subplot(df=tp_df, ax=ax_tp, x_col='thread_cnt', y_col='throughput',
                 z_col='cc_alg', x_range=thread_cnts, z_range=cc_algs,
                 filters={"num_wh": 1})

    # plot tail latency
    tail_df = pd.read_csv(f"results/{exper}/tail.csv", header=0,
                          na_values="None", skipinitialspace=True)
    make_subplot(df=tail_df, ax=ax_tail, x_col='thread_cnt', y_col=tail_metric,
                 z_col='cc_alg', x_range=thread_cnts, z_range=cc_algs,
                 filters={"num_wh": 1, 'tag': 'all'})

    ax_tp.set_xlabel('Number of threads')
    ax_tail.set_xlabel('Number of threads')

    ax_tp.set_xticks([1, 8, 16, 32, 48, 64])
    ax_tail.set_xticks([1, 8, 16, 32, 48, 64])
    ax_tp.set_xlim(0)
    ax_tail.set_xlim(0)

    return fig, (ax_tp, ax_tail)


def plot_tpcc_warehouse_vs_throughput_tail(exper: str, tail_metric='p999', layout='LR'):
    assert layout in {"LR", "UD"}
    fig, (ax_tp, ax_tail) = get_subplots_LR() \
        if layout == 'LR' else get_subplots_UD()

    cc_algs = ["NO_WAIT", "WAIT_DIE", "WOUND_WAIT", "SILO", "SILO_PRIO"]
    num_wh_range = [1, 8, 16, 32, 64]

    # plot throughput
    tp_df = pd.read_csv(f"results/{exper}/throughput.csv", header=0,
                        na_values="None", skipinitialspace=True)
    make_subplot(df=tp_df, ax=ax_tp, x_col='num_wh', y_col='throughput',
                 z_col='cc_alg', x_range=num_wh_range, z_range=cc_algs,
                 filters={"thread_cnt": 64})

    # plot tail latency
    tail_df = pd.read_csv(f"results/{exper}/tail.csv", header=0,
                          na_values="None", skipinitialspace=True)
    make_subplot(df=tail_df, ax=ax_tail, x_col='num_wh', y_col=tail_metric,
                 z_col='cc_alg', x_range=num_wh_range, z_range=cc_algs,
                 filters={"thread_cnt": 64, 'tag': 'all'})

    ax_tp.set_xticks(num_wh_range)
    ax_tail.set_xticks(num_wh_range)

    ax_tp.set_xlabel('Number of warehouses')
    ax_tail.set_xlabel('Number of warehouses')

    ax_tp.set_xticks([1, 8, 16, 32, 48, 64])
    ax_tail.set_xticks([1, 8, 16, 32, 48, 64])
    ax_tp.set_xlim(0)
    ax_tail.set_xlim(0)

    return fig, (ax_tp, ax_tail)


def plot_ycsb_prio_ratio_vs_throughput(exper: str):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    set_fig(fig, [FIG_SIZE[0] // 1.5, FIG_SIZE[1]])

    pr_range = [0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    tp_df = pd.read_csv(f"results/{exper}/throughput.csv", header=0,
                        na_values="None", skipinitialspace=True)
    make_subplot(df=tp_df, ax=ax, x_col='prio_ratio', y_col='throughput',
                 z_col='cc_alg', x_range=pr_range, z_range=["SILO_PRIO"],
                 filters={"zipf_theta": 0.99})

    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    ax.set_xlabel('High priority transaction ratio')

    return fig, ax


def plot1():
    fig, (ax_tp, ax_tail) = plot_ycsb_thread_vs_throughput_tail("ycsb_thread")

    tp_ticks = list(range(0, 600001, 100000))
    ax_tp.set_yticks(
        tp_ticks, [f"{t/1e6}" if t > 0 else "0" for t in tp_ticks], rotation=90)
    ax_tp.set_ylim([0, 600000])

    tail_ticks = list(range(0, 1601, 400))
    ax_tail.set_yticks(
        tail_ticks, [f"{t/1e3}" if t > 0 else "0" for t in tail_ticks], rotation=90)
    ax_tail.set_ylim([0, 1600])

    ax_tp.set_ylabel('Throughput (Mtxn/s)')
    ax_tail.set_ylabel(f'Tail latency p999 (ms)')

    fig.savefig(
        f"ycsb_thread_vs_throughput_tail.{IMAGE_TYPE}", transparent=True)


def plot2():
    fig, (ax_tp, ax_tail) = plot_ycsb_zipf_vs_throughput_tail("ycsb_zipf")
    fig.savefig(f"ycsb_zipf_vs_throughput_tail.{IMAGE_TYPE}",
                transparent=True)


def plot3():
    fig, (ax_tp, ax_tail) = plot_ycsb_thread_vs_throughput_tail("ycsb_longtxn")

    tp_ticks = list(range(0, 160001, 40000))
    ax_tp.set_yticks(
        tp_ticks, [f"{t/1e6}" if t > 0 else "0" for t in tp_ticks], rotation=90)
    ax_tp.set_ylim([0, 160000])

    tail_ticks = list(range(0, 16001, 4000))
    ax_tail.set_yticks(
        tail_ticks, [f"{t//1e3}" if t > 0 else "0" for t in tail_ticks], rotation=90)
    ax_tail.set_ylim([0, 16000])

    fig.savefig(
        f"ycsb_longtxn_thread_vs_throughput_tail.{IMAGE_TYPE}", transparent=True)


def plot4():
    fig, (ax_tail, ax_tp) = plot_latency_logscale_throughput("ycsb_udprio")
    tp_ticks = list(range(0, 600001, 100000))
    ax_tp.set_yticks(
        tp_ticks, [f"{t/1e6}" if t > 0 else "0" for t in tp_ticks], rotation=90)
    ax_tp.set_ylim([0, 600000])
    fig.savefig(
        f"ycsb_latency_logscale_throughput.{IMAGE_TYPE}", transparent=True)


def plot5():
    fig, (ax_tp, ax_tail) = plot_tpcc_thread_vs_throughput_tail("tpcc_thread")

    tp_ticks = list(range(0, 300001, 100000))
    ax_tp.set_yticks(
        tp_ticks, [f"{t/1e6}" if t > 0 else "0" for t in tp_ticks], rotation=90)
    ax_tp.set_ylim([0, 300000])

    tail_ticks = list(range(0, 2001, 500))
    ax_tail.set_yticks(
        tail_ticks, [f"{t/1e3}" if t > 0 else "0" for t in tail_ticks], rotation=90)
    ax_tail.set_ylim([0, 2000])

    ax_tp.set_ylabel('Throughput (Mtxn/s)')
    ax_tail.set_ylabel(f'Tail latency p999 (ms)')

    fig.savefig(
        f"tpcc_thread_vs_throughput_tail.{IMAGE_TYPE}", transparent=True)


def plot6():
    fig, (ax_tp, ax_tail) = plot_tpcc_warehouse_vs_throughput_tail("tpcc_wh")

    tp_ticks = list(range(0, 4000001, 1000000))
    ax_tp.set_yticks(
        tp_ticks, [f"{t//1000000}" if t > 0 else "0" for t in tp_ticks], rotation=90)
    ax_tp.set_ylim([0, 4000000])

    ax_tp.set_xticks([1, 8, 16, 32, 64])
    ax_tail.set_xticks([1, 8, 16, 32, 64])
    # ax_tp.set_xscale('log')
    # ax_tail.set_xscale('log')

    tail_ticks = list(range(0, 4001, 1000))
    ax_tail.set_yticks(
        tail_ticks, [f"{t//100}" if t > 0 else "0" for t in tail_ticks], rotation=90)
    ax_tail.set_ylim([0, 4000])

    ax_tp.set_ylabel('Throughput (Mtxn/s)')
    ax_tail.set_ylabel(f'Tail latency p999 (ms)')
    fig.savefig(
        f"tpcc_warehouse_vs_throughput_tail.{IMAGE_TYPE}", transparent=True)


def plot7():
    fig, ax = plot_ycsb_prio_ratio_vs_throughput("ycsb_prio_sen")

    tp_ticks = list(range(0, 500001, 100000))
    ax.set_yticks(
        tp_ticks, [f"{t/1e6}" if t > 0 else "0" for t in tp_ticks], rotation=90)
    ax.set_ylim([0, 500000])
    ax.set_ylabel('Throughput (Mtxn/s)')

    fig.savefig(
        f"ycsb_prio_ratio_vs_throughput.{IMAGE_TYPE}", transparent=True)


plot1()
plot2()
plot3()
plot4()
plot5()
plot6()
plot7()
