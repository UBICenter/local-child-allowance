import pandas as pd

block = pd.read_csv(
    "data/master_block.csv.gz",
    usecols=[
        "puma",
        "state_fip",
        "lower_leg_district",
        "upper_leg_district",
        "P001001",
    ],
)
# Limit to blocks with population.
block = block[block.P001001 > 0]

PUMA_KEYS = ["state_fip", "puma"]

puma_pop = (
    block.groupby(PUMA_KEYS)[["P001001"]]
    .sum()
    .rename(columns={"P001001": "puma_pop"})
    .reset_index()
)


def write_puma_intersection(key, fname):
    puma_leg = (
        block.groupby(PUMA_KEYS + key)[["P001001"]]
        .sum()
        .reset_index()
        .merge(puma_pop, on=PUMA_KEYS)
    )

    puma_leg["share_of_puma_pop"] = puma_leg.P001001 / puma_leg.puma_pop

    puma_leg.to_csv("data/" + fname + ".csv", index=False)


write_puma_intersection(
    ["lower_leg_district", "upper_leg_district"],
    "puma_upper_lower_leg_district",
)
write_puma_intersection(["lower_leg_district"], "puma_lower_leg_district")
write_puma_intersection(["upper_leg_district"], "puma_upper_leg_district")
