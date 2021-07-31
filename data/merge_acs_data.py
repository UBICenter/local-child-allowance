import pandas as pd

# Read in two files - one, a population by geography file produced by NHGIS
# The data can be found with these filters:
# DATASETS : 	2015_2019_ACS5a
# TOPICS : Total Population
# The data should be downloaded at the block group level, the highest resolution geo data available from the ACS

# The second file is our master block data set, which is produced elsewhere in this repository.
# See 'create_master_block_dataset.py'


acs_block_groups = pd.read_csv(
    "data/original/nhgis/nhgis0002_csv/nhgis0002_ds244_20195_2019_blck_grp.csv",
    usecols=[
        "YEAR",
        "STATEA",
        "COUNTYA",
        "TRACTA",
        "BLKGRPA",
        "NAME_E",
        "ALUBE001",
        "ALUBM001",
    ],
)

# low_memory = False is necessary to avoid an error message when loading in the huge block-level data

blocks = pd.read_csv("data/master_block.csv.gz", low_memory=False,)


# Fill missing values that interfere with merge with 0

blocks.fillna(0, inplace=True)


# The blockgroup is the same as the first digit of the four digit block number.
# Therefore, we can obtain it by integer dividing by 1000

blocks["block_group"] = blocks.block // 1000


# Here we aggregate our block level data up to the block group level, so that we can then join it with the ACS data,
# which is also at the block group level


MERGE_COLS = ["state_fip", "county_fip", "census_tract", "block_group"]

block_group = blocks.groupby(MERGE_COLS)[["population"]].sum().reset_index()


# Renaming columns to simplify merging

acs_block_groups.rename(
    columns={
        "STATEA": "state_fip",
        "COUNTYA": "county_fip",
        "TRACTA": "census_tract",
        "BLKGRPA": "block_group",
        "NAME_E": "acs_name",
        "ALUBE001": "acs_population",
        "ALUBM001": "acs_pop_moe",
    },
    inplace=True,
)


# Merging the ACS and aggregated block data

acs_block_data = pd.merge(
    acs_block_groups, block_group, on=MERGE_COLS, how="outer",
)


# Finding the percentage change in population in each block group from 2010 to 2019 using ACS data

acs_block_data["block_group_adjustment_factor"] = (
    acs_block_data.acs_population / acs_block_data.population
)


# Using integer division once again to find the block group of a given block

blocks["block_group"] = blocks.block // 1000


# Merging the acs block group level data back onto the more detailed block level data we started with.
# This will allow us to apply the adjustment factor that we found above to all of the blocks within a block group

adjusted_blocks = acs_block_data.merge(blocks, on=MERGE_COLS, how="outer")


# Renaming for simplicity

adjusted_blocks.rename(
    columns={
        "acs_population": "acs_bg_pop_2019",
        "population_x": "total_bg_pop_2010",
        "population_y": "block_pop_2010",
    },
    inplace=True,
)


# Finding block-level adjusted population using the adjustment factor from the ACS 2019 data

adjusted_blocks["block_pop_adj_2019"] = (
    adjusted_blocks["block_pop_2010"]
    * adjusted_blocks["block_group_adjustment_factor"]
)

assert (
    adjusted_blocks.block_pop_adj_2019.sum()
    > adjusted_blocks.block_pop_2010.sum()
)

assert (
    adjusted_blocks.acs_bg_pop_2019.sum()
    > adjusted_blocks.total_bg_pop_2010.sum()
)

total_pop = int(adjusted_blocks.block_pop_adj_2019.sum())

assert 330e6 > total_pop > 324e6


# Exporting to .csv.gz

adjusted_blocks.to_csv(
    "data/master_block_2019_adjusted.csv.gz", compression="gzip"
)
