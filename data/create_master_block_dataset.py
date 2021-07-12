import pandas as pd

# Load data.
block = pd.read_csv("data/raw/census_block.csv.gz").rename(
    columns={
        "STATE": "state_fip",
        "COUNTY": "county_fip",
        "TRACT": "census_tract",
        "BLOCK": "block",
    }
)
lower_state_district = pd.read_csv(
    "data/raw/National_2018SLDL.txt.gz", dtype="str"
).rename(columns={"DISTRICT": "lower_leg_district"})
upper_state_district = pd.read_csv(
    "data/raw/National_2018SLDU.txt.gz", dtype="str"
).rename(columns={"DISTRICT": "upper_leg_district"})
tract_to_puma = pd.read_csv(
    "data/raw/2010_Census_Tract_to_2010_PUMA.txt.gz"
).rename(
    columns={
        "STATEFP": "state_fip",
        "COUNTYFP": "county_fip",
        "TRACTCE": "census_tract",
        "PUMA5CE": "puma",
    },
)

# Preprocess data.
# Deconstruct BLOCKID into block/tract/county/state
state_district = lower_state_district.merge(upper_state_district, on="BLOCKID")
state_district["state_fip"] = state_district.BLOCKID.str[0:2]
state_district["county_fip"] = state_district.BLOCKID.str[2:5]
state_district["census_tract"] = state_district.BLOCKID.str[5:11]
state_district["block_group"] = state_district.BLOCKID.str[11]
state_district["block"] = state_district.BLOCKID.str[11:15]

# Merge data.
JOIN_COLUMNS = ["state_fip", "county_fip", "census_tract", "block"]

block[JOIN_COLUMNS] = block[JOIN_COLUMNS].astype(int)

state_district[JOIN_COLUMNS] = state_district[JOIN_COLUMNS].astype(int)

# Merge the master block dataset to state leg districts.
block = pd.merge(block, state_district, how="outer", on=JOIN_COLUMNS)

# Merge to PUMA file.
block = block.merge(
    tract_to_puma, on=["state_fip", "county_fip", "census_tract"], how="outer"
)

# Export.
OUT_COLS = [
    "state_fip",
    "county_fip",
    "census_tract",
    "puma",
    "block",
    "P001001",
    "lower_leg_district",
    "upper_leg_district",
]
block[OUT_COLS].to_csv(
    "data/master_block.csv.gz", index=False, compression="gzip"
)
