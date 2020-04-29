import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os

EXPERIMENT_PATH = "experiments"
try:
    os.mkdir(EXPERIMENT_PATH)
except:
    pass


def plot_record(
    record,
    values=["total fitness", "f dist", "f symm", "f age", "age", "order"],
    title="record",
    plot_name=None,
    playing_only=False,
    sharey=True,
    step=30,
):
    """Plots selected columns of the experiment record over generations"""

    fig, axes = plt.subplots(
        len(values), 1, sharey=sharey, sharex=True, figsize=(8, 12)
    )
    fig.suptitle(title, fontsize=16)

    if playing_only:
        record = record.loc[record["playing"]]

    if step:
        n_gen = record["generation"].max()
        xticks = np.arange(0, n_gen + 1, step)

    for i, v in enumerate(values):
        for xc in xticks:
            axes[i].axvline(x=xc, color="k", linestyle="--", alpha=0.2)
        if i == 0:
            sns.lineplot(
                data=record,
                x="generation",
                y=v,
                hue="population",
                ci=None,
                alpha=0.5,
                ax=axes[i],
            )
            sns.lineplot(data=record, x="generation", y=v, ax=axes[i], color="black")
        else:
            sns.lineplot(
                data=record,
                x="generation",
                y=v,
                hue="population",
                ci=None,
                alpha=0.5,
                ax=axes[i],
                legend=False,
            )
            sns.lineplot(
                data=record,
                x="generation",
                y=v,
                ax=axes[i],
                color="black",
                legend=False,
            )

    if n_gen >= 2 * step:
        plt.xticks(xticks)

    axes[0].legend(
        bbox_to_anchor=(0, 1.05, 1, 0.2),
        loc="lower left",
        mode="expand",
        borderaxespad=0,
        ncol=4,
        fancybox=True,
    )

    if plot_name is not None:
        try:
            plot_path = os.path.join(EXPERIMENT_PATH, plot_name)
            plt.savefig(plot_path + ".png")
            print(f"saved plot at {plot_path}")
        except:
            print(f"could not save figure at {plot_path}")
    else:
        plt.show()
    plt.close()


if __name__ == "__main__":
    """Plots the results of a past experiment"""
    experiment_number = 2

    result_path = os.path.join(
        EXPERIMENT_PATH, f"experiment{experiment_number}_record.csv"
    )
    record = pd.read_csv(result_path)

    plot_record(
        record,
        title="Population average",
        plot_name=f"experiment{experiment_number}_population",
        playing_only=False,
    )

    plot_record(
        record,
        title="Playing only",
        plot_name=f"experiment{experiment_number}_playing.png",
        playing_only=True,
    )

    parameters = [
        "w symm",
        "w age",
        "w dist",
        "target order",
        "mut rate",
        "rootnote",
    ]

    plot_record(
        record,
        title="Parameters",
        values=parameters,
        plot_name=f"experiment{experiment_number}_parameters",
        playing_only=False,
        sharey=False,
    )
