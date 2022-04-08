import matplotlib.pyplot as plt
import numpy as np
from skimage.io import imread

import smo

from . import common

# Image
image = imread("data/image.tif")
image = image[:300, 200:]  # crop image

# Manual selection of background
x0, x1, y0, y1 = 0, 80, 80, 130
bg_manual = slice(y0, y1), slice(x0, x1)

# SMO pre-smoothing parameter
sigma = 1


sizes = (2, 5, 20, 50, 100)

cmap = plt.get_cmap("viridis")
sizes = {s: cmap(c) for s, c in zip(sizes, np.linspace(0, 1, len(sizes)))}

fig = plt.figure()
fig.set_figheight(2.5)
top, bottom = fig.add_gridspec(2, 1, height_ratios=(1, 1.5))
axes_images = top.subgridspec(1, 5).subplots()
left, right = bottom.subgridspec(1, 2, width_ratios=(2, 1), wspace=0.5)
axes_pdf = left.subgridspec(1, 2, wspace=0.4).subplots()
axes_cdf = fig.add_subplot(right)

axes_hists = {
    axes_cdf: {"cumulative": True},
    axes_pdf[0]: {"cumulative": False},
    axes_pdf[1]: {"cumulative": False},
}

axes_pdf[0].set(ylabel="PDF")
axes_pdf[1].set(yscale="log")
axes_cdf.set(ylabel="CDF")

for ax in axes_hists:
    ax.set(xlabel="Intensity [a.u.]")

bins = np.arange(198, 220)

for ax, hist_kw in axes_hists.items():
    ax.hist(
        image[bg_manual].flat,
        bins=bins,
        density=True,
        color="gray",
        alpha=0.5,
        label="Ground\ntruth",
        **hist_kw,
    )

for ax, (size, color) in zip(axes_images, sizes.items()):
    smo_image = smo.smo(image, sigma=sigma, size=size)
    smo_rv = smo.smo_rv((1024, 1024), sigma=sigma, size=size)
    bg_dist = image[smo_image < smo_rv.ppf(0.05)]

    ax.imshow(smo_image, cmap=common.cmap.smo, rasterized=True)

    for ax_h, hist_kw in axes_hists.items():
        ax_h.hist(
            bg_dist, bins=bins, density=True, histtype="step", color=color, **hist_kw
        )

    ax.add_patch(
        plt.Rectangle((80, 100), size, size, facecolor="none", edgecolor="red")
    )
    ax.set(xticks=(), yticks=(), title=f"{size}x{size}")
    for spine in ax.spines.values():
        spine.set(color=color, linewidth=3)

axes_cdf.legend(loc="lower right", fontsize="small")

common.save_or_show(fig, "suppfig2")
