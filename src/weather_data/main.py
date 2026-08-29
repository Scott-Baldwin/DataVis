# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "polars",
#   "psychrolib",
# ]
# ///

# standard lib
# import os
from pathlib import Path

# 3rd party lib
import polars as pl
import psychrolib

# custom
from html_viewer import create_3d_scatter_viewer

# set unit system
psychrolib.SetUnitSystem(psychrolib.SI)


def read_file(path: str | Path) -> tuple[pl.DataFrame, dict]:
    # get info from top 2 rows of headers
    info = pl.read_csv(path, n_rows=2).to_dicts()[0]
    # get data
    df = pl.read_csv(path, skip_rows=2)

    # check & convert pressures to pascals (Pa)
    pressure_unit = info["Pressure Units"]
    # default tmy units in mbar
    if pressure_unit == "mbar":
        # multiply by 100 to get Pa
        df = df.with_columns(pl.col("Pressure").mul(100).alias("Pressure"))
        info["Pressure Units"] = "Pa"
    # break for unhandled unit
    elif pressure_unit != "Pa":
        raise ValueError(f"Unexpected Pressure Units: {pressure_unit}")

    # check & convert relative humidity
    humidity_unit = info["Relative Humidity Units"]
    if humidity_unit == "%":
        # convert from percent (0-100) to decimal (0-1)
        df = df.with_columns(
            pl.col("Relative Humidity").mul(0.01).alias("Relative Humidity")
        )
        info["Relative Humidity Units"] = "0-1"
    # break for unhandled unit
    elif humidity_unit != "0-1":
        raise ValueError(f"Unexpected Relative Humidity Units: {humidity_unit}")

    # TODO: add checks for temperature units

    return df, info


def calc_wet_bulb(row: dict) -> float:
    return psychrolib.GetTWetBulbFromRelHum(
        row["Temperature"], row["Relative Humidity"], row["Pressure"]
    )


def calc_enthalpy(row: dict) -> float:
    return psychrolib.GetMoistAirEnthalpy(
        row["Temperature"],
        psychrolib.GetHumRatioFromRelHum(
            row["Temperature"], row["Relative Humidity"], row["Pressure"]
        ),
    )


def calc_enthalpy_sat(row: dict) -> float:
    # get enthalpy at 100% relative humidity
    return psychrolib.GetMoistAirEnthalpy(
        row["Temperature"],
        psychrolib.GetHumRatioFromRelHum(row["Temperature"], 1.0, row["Pressure"]),
    )


def main() -> None:
    parent_path = Path(__file__).parent
    data_path = parent_path / "data" / "nyc-tmy-2023.csv"

    df, info = read_file(data_path)

    df = df.with_columns(
        pl.struct("Temperature", "Relative Humidity", "Pressure")
        .map_elements(calc_wet_bulb, return_dtype=pl.Float64)
        .alias("Wet Bulb")
    )

    df = df.with_columns(
        pl.struct("Temperature", "Relative Humidity", "Pressure")
        .map_elements(calc_enthalpy, return_dtype=pl.Float64)
        .alias("Enthalpy")
    )

    df = df.with_columns(
        pl.struct("Temperature", "Relative Humidity", "Pressure")
        .map_elements(calc_enthalpy_sat, return_dtype=pl.Float64)
        .alias("Enthalpy_100RH")
    )

    print(df)

    # one percent wet bulb
    one_pct_wb = df.select(pl.col("Wet Bulb").quantile(0.99)).item()

    # mean coincident dry bulb
    mc_db = (
        df.filter(pl.col("Wet Bulb") >= one_pct_wb)
        .select(pl.col("Temperature").mean())
        .item()
    )

    temp_unit = info["Temperature Units"]
    print(f"1% Wet Bulb [{temp_unit}]: {round(one_pct_wb, 1)}")
    print(f"Mean Coincident Dry Bulb [{temp_unit}]: {round(mc_db, 1)}")

    # # export to 3d viewer
    # # pull these columns to the front to use for default setup
    # first_columns = ["Temperature", "Wind Direction", "Wind Speed", "Month"]
    # all_columns = df.columns
    # other_columns = [col for col in all_columns if col not in first_columns]
    #
    # # Create the new column order
    # new_column_order = first_columns + other_columns
    #
    # # Apply select to reorder the DataFrame
    # out_path = parent_path / "3d_plot.html"
    # create_3d_scatter_viewer(df.select(new_column_order), out_path)


# %%
if __name__ == "__main__":
    main()
