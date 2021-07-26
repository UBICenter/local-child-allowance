import pandas as pd
import numpy as np

# Read in two files - one, a population by geography file produced by NHGIS
# The data can be found with these filters:
# DATASETS : 	2015_2019_ACS5a
# TOPICS : Total Population
# The data should be downloaded at the block group level, the highest resolution geo data available from the ACS

# The second file is our master block data set, which is produced elsewhere in this repository.
# See 'create_master_block_dataset.py'


acs = pd.read_csv(
    r"C:\UBICenter\local-child-allowance\data\original\nhgis\nhgis0002_ds244_20195_2019_blck_grp.csv",
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

blocks = pd.read_csv(
    r"C:\UBICenter\local-child-allowance\data\master_block.csv.gz",
    low_memory=False,
)


# Fill missing values that interfere with merge with 0

blocks.fillna(0)


# The blockgroup is the same as the first digit of the four digit block number. Therefore, we can obtain it by integer dividing
# 1000

blocks["block_group"] = (blocks["block"]) // 1000


# Here we aggregate our block level data up to the block group level, so that we can then join it with the ACS data,
# which is also at the block group level

block_group = (
    blocks.groupby(["state_fip", "county_fip", "census_tract", "block_group"])[
        ["population"]
    ]
    .sum()
    .reset_index()
)


# Renaming columns to simplify merging

acs.rename(
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
    acs,
    block_group,
    on=["state_fip", "county_fip", "census_tract", "block_group"],
    how="outer",
)


# Finding the percentage change in population in each block group from 2010 to 2019 using ACS data

acs_block_data["block_group_adjustment_factor"] = (
    acs_block_data["acs_population"] / acs_block_data["population"]
)


# Using integer division once again to find the block group of a given block

blocks["block_group"] = blocks["block"] // 1000


# Merging the acs block group level data back onto the more detailed block level data we started with.
# This will allow us to apply the adjustment factor that we found above to all of the blocks within a block group

adjusted_blocks = pd.merge(
    acs_block_data,
    blocks,
    on=["state_fip", "county_fip", "census_tract", "block_group"],
    how="outer",
)


# Renaming for simplicity

adjusted_blocks = adjusted_blocks.rename(
    columns={
        "acs_population": "acs_bg_population_2019",
        "population_x": "total_bg_pop_2010",
        "population_y": "block_population_2010",
    }
)


# Finding block-level adjusted population using the adjustment factor from the ACS 2019 data

adjusted_blocks["block_population_adj_2019"] = (
    adjusted_blocks["block_population_2010"]
    * adjusted_blocks["block_group_adjustment_factor"]
)

# Exporting to .csv.gz

adjusted_blocks.to_csv("master_block_2019_adjusted.csv.gz", compression="gzip")
