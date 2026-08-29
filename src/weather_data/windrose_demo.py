import os
from matplotlib import cm

import polars as pl

# import pandas as pd
import matplotlib.pyplot as plt
from windrose import WindroseAxes, WindAxes

# 1. Read meteorological data
file_path = os.path.join(
    os.path.dirname(__file__),
    "data",
    "nyc-tmy-2023.csv",
)

df = pl.read_csv(file_path, skip_rows=2)

# windrose works best with numpy arrays
wd = df["Wind Direction"].to_numpy()
ws = df["Wind Speed"].to_numpy()
temp = df["Temperature"].to_numpy()

# 2. Initialize the figure
fig = plt.figure(figsize=(8, 8))
ax = WindroseAxes.from_ax(fig=fig)

# 3. Create the wind rose
# 'kind' can be 'bar' (default) or 'contour'
# bins = [-10, 0, 10, 20, 25, 30]  # temperature bins
nsector = 24  # 15 deg steps
# low_cutoff = -10


ax.contourf(
    wd,
    temp,
    normed=True,
    # bins=bins,
    cmap=cm.coolwarm,  # pyright: ignore[reportAttributeAccessIssue]
    nsector=nsector,
    # calm_limit=low_cutoff,
)
ax.contour(
    wd,
    temp,
    normed=True,
    # bins=bins,
    colors="black",
    nsector=nsector,
    # calm_limit=low_cutoff,
)


# 4. Add styling and legend
ax.set_legend()
plt.title("Wind Rose: Temperature and Direction Distribution")
# plt.tight_layout()
plt.show()
