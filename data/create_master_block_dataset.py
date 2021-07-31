from typing import Union
import pandas as pd

# Load data.
def load(
    path: str, columns: Union[list, dict] = None, **kwargs
) -> pd.DataFrame:
    """Load file.

    :param path: File within data/raw/
    :type path: str
    :param columns: List of columns or dict of columns to load and rename.
    :type columns: Union[list, dict], optional
    :return: DataFrame
    :rtype: DataFrame
    """
    path = "data/raw/" + path
    if isinstance(columns, dict):
        return pd.read_csv(
            path, usecols=list(columns.keys()), **kwargs
        ).rename(columns=columns)
    return pd.read_csv(path, usecols=columns, **kwargs)


block = load(
    "census_block.csv.gz",
    columns={
        "STATE": "state_fip",
        "COUNTY": "county_fip",
        "TRACT": "census_tract",
        "BLOCK": "block",
        "P001001": "population_2010",
    },
)

lower_state_district = load(
    "National_2018SLDL.txt.gz",
    dtype="str",
    columns={"BLOCKID": "BLOCKID", "DISTRICT": "lower_leg_district"},
)

upper_state_district = load(
    "National_2018SLDU.txt.gz",
    dtype="str",
    columns={"BLOCKID": "BLOCKID", "DISTRICT": "upper_leg_district"},
)

tract_to_puma = load(
    "2010_Census_Tract_to_2010_PUMA.txt.gz",
    columns={
        "STATEFP": "state_fip",
        "COUNTYFP": "county_fip",
        "TRACTCE": "census_tract",
        "PUMA5CE": "puma",
    },
)

acs_block_group = load(
    "nhgis/nhgis0002_csv/nhgis0002_ds244_20195_2019_blck_grp.csv",
    columns={
        "STATEA": "state_fip",
        "COUNTYA": "county_fip",
        "TRACTA": "census_tract",
        "BLKGRPA": "block_group",
        "ALUBE001": "acs_population",
    },
)

# Preprocess data.
# Deconstruct BLOCKID into block/tract/county/state
state_district = lower_state_district.merge(
    upper_state_district, on="BLOCKID", how="outer"
)
state_district["state_fip"] = state_district.BLOCKID.str[0:2]
state_district["county_fip"] = state_district.BLOCKID.str[2:5]
state_district["census_tract"] = state_district.BLOCKID.str[5:11]
state_district["block_group"] = state_district.BLOCKID.str[11].astype(int)
state_district["block"] = state_district.BLOCKID.str[11:15]

# Merge data.
JOIN_COLUMNS = ["state_fip", "county_fip", "census_tract", "block"]

block[JOIN_COLUMNS] = block[JOIN_COLUMNS].astype(int)

state_district[JOIN_COLUMNS] = state_district[JOIN_COLUMNS].astype(int)

# Merge the master block dataset to state leg districts.
block = pd.merge(block, state_district, how="outer", on=JOIN_COLUMNS)

# Merge to PUMA file and fill missing values that interfere with later merges.
block = block.merge(
    tract_to_puma, on=["state_fip", "county_fip", "census_tract"], how="outer"
).fillna(0)

# Aggregate block level data to the block group level, so that we can then
# join it with the ACS data, which is also at the block group level.
MERGE_COLS = ["state_fip", "county_fip", "census_tract", "block_group"]

# Merge the ACS and aggregated block data.
block_group = pd.merge(
    block.groupby(MERGE_COLS)[["population_2010"]].sum().reset_index(),
    acs_block_group,
    on=MERGE_COLS,
    how="outer",
)

# Find the percentage change in population in each block group from 2010 to
# 2019 using ACS data.
block_group["block_group_adjustment_factor"] = (
    block_group.acs_population / block_group.population_2010
)

# Merge the ACS block group level data back onto the more detailed block level
# data we started with. This will allow us to apply the adjustment factor that
# we found above to all of the blocks within a block group.
block = block.merge(
    block_group.drop(columns="population_2010"), on=MERGE_COLS, how="outer"
)

# Adjust block-level population using adjustment factor from ACS 2019 data.
block["population"] = (
    block.population_2010 * block.block_group_adjustment_factor
)

# Check that population increases since 2010 and is within the expected range.
assert block.population.sum() > block.population_2010.sum()
assert 330e6 > block.population.sum() > 324e6

# Export.
OUT_COLS = [
    "state_fip",
    "county_fip",
    "census_tract",
    "puma",
    "block",
    "population",
    "lower_leg_district",
    "upper_leg_district",
]
block[OUT_COLS].to_csv(
    "data/master_block.csv.gz", index=False, compression="gzip"
)
