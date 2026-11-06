from pathlib import Path
from typing import Optional, Union

import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

PathLike = Union[str, Path]


def apply_theme() -> None:
    """Apply the library's Seaborn theme globally."""
    sns.set_theme(style="darkgrid", rc={"axes.facecolor": ".9"})


def style_axis(
    ax: Axes,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
) -> None:
    """Set a bold title and axis labels on ``ax``."""
    ax.set(xlabel=xlabel, ylabel=ylabel)
    if title:
        ax.set_title(title, fontdict={"fontsize": 14, "fontweight": "bold"})


def finish_plot(
    fig: Figure,
    filename: Optional[str] = None,
    save_directory: Optional[PathLike] = None,
    show: bool = True,
) -> Figure:
    """
    Tidy the layout, optionally save the figure, optionally show it,
    and return it. The save directory is created if it does not exist.
    """
    fig.tight_layout()
    if filename is not None:
        directory = Path(save_directory) if save_directory is not None else Path.cwd()
        directory.mkdir(parents=True, exist_ok=True)
        fig.savefig(directory / filename)
    if show:
        plt.show()
    return fig