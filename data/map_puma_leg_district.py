import pandas as pd

block = pd.read_csv(
    "data/master_block.csv.gz",
    usecols=[
        "puma",
        "county_fip",
        "state_fip",
        "lower_leg_district",
        "upper_leg_district",
        "population",
    ],
    dtype={"lower_leg_district": str, "upper_leg_district": str},
)
# Limit to blocks with population.
block = block[block.population > 0]

# Fill NA values in the master_block file

block.fillna(0, inplace=True)

PUMA_KEYS = ["state_fip", "puma"]

puma_pop = (
    block.groupby(PUMA_KEYS)[["population"]]
    .sum()
    .rename(columns={"population": "puma_pop"})
    .reset_index()
)


def write_puma_intersection(key, fname):
    puma_leg = (
        block.groupby(PUMA_KEYS + key)[["population"]]
        .sum()
        .reset_index()
        .merge(puma_pop, on=PUMA_KEYS)
    )

    puma_leg["share_of_puma_pop"] = puma_leg.population / puma_leg.puma_pop

    puma_leg.to_csv("data/" + fname + ".csv", index=False)


write_puma_intersection(
    ["lower_leg_district", "upper_leg_district"], "puma_upper_lower_leg_district",
)
write_puma_intersection(["lower_leg_district"], "puma_lower_leg_district")
write_puma_intersection(["upper_leg_district"], "puma_upper_leg_district")
write_puma_intersection(["county_fip"], "puma_county")
