# not used yet, jst in place to check that libraries are installed
import polars as pl
import psychrolib

# set unit system
psychrolib.SetUnitSystem(psychrolib.SI)


def read_file(path="data/nyc-tmy-2023.csv"):
    # get data
    df = pl.read_csv(path, skip_rows=2)

    # TODO: check data file info for correct units
    # get info from top 2 rows of headers
    # info = pl.read_csv(path, n_rows=2).to_dicts()[0]
    # print(info)

    # convert units in tmy data file to units used in psychrolib functions
    df = df.with_columns(
        # convert humidity as percent (0-100) to decimal (0-1)
        pl.col("Relative Humidity").mul(0.01).alias("Relative Humidity"),
        # convert pressure as millibar (mbar) to pascals (pa)
        pl.col("Pressure").mul(100).alias("Pressure"),
    )
    return df


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


def main():
    df = read_file()
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

    # print(out.select(pl.all()).filter(pl.col("Wet Bulb") > 22))
    # print(df.select(pl.col("Wet Bulb").quantile(0.99)))
    print(df)


# %%
if __name__ == "__main__":
    main()
