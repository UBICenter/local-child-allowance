import pandas as pd
import censusdata

# variables to download from the census api package can be viewed here:
# https://api.census.gov/data/2010/dec/sf1/variables/

# NB: This can't be directly downloaded from the Census website because they 
# only have data for each state.

l = []

STATE_FIPS_REMOVE = [5, 7, 14, 43, 52]
# Including DC.
state_fips = [i for i in [*range(1, 57)] if i not in STATE_FIPS_REMOVE]

for i in state_fips:
    l.append(
        censusdata.download(
            "sf1",
            2010,
            censusdata.censusgeo(
                [
                    ("state", str(i).zfill(2)),
                    ("county", "*"),
                    ("tract", "*"),
                    ("block", "*"),
                ]
            ),
            ["STATE", "COUNTY", "TRACT", "BLOCK", "P001001"],
        )
    )

all_blocks = pd.concat(l)

all_blocks.to_csv("data/raw/census_block.csv.gz", index=False, compression="gzip")
