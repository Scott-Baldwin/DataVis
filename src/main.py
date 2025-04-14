# not used yet, jst in place to check that libraries are installed
import polars as pl
import psychrolib

psychrolib.SetUnitSystem(psychrolib.SI)
file_path = "data/nyc-tmy-2023.csv"


# get info from top 2 rows of headers
info = pl.read_csv(file_path, n_rows=2).to_dicts()[0]

# get data
df = pl.read_csv(file_path, skip_rows=2)


def calc_wet_bulb(t_dry: float, percent_hum: float, pres_mbar: int) -> float:
    # convert units from tmy data units to psychrolib units
    # TODO: check data file info for correct units
    rel_hum = percent_hum / 100
    press_pa = pres_mbar * 100
    return psychrolib.GetTWetBulbFromRelHum(t_dry, rel_hum, press_pa)


out = df.with_columns(
    pl.struct("Temperature", "Relative Humidity", "Pressure")
    .map_elements(
        lambda x: calc_wet_bulb(
            x["Temperature"], x["Relative Humidity"], x["Pressure"]
        ),
        return_dtype=pl.Float64,
    )
    .alias("Wet Bulb")
)

print(out.select(pl.all()).filter(pl.col("Wet Bulb") > 22))
