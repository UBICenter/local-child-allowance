import pandas as pd
import censusdata

# variables to download from the census api package can be viewed here:
# https://api.census.gov/data/2010/dec/sf1/variables/

# NB: This can't be directly downloaded from the Census website because they
# only have data for each state.

l = []

STATE_FIPS_REMOVE = [3, 7, 14, 43, 52]
# Including DC.
all_state_fips = [i for i in [*range(1, 57)] if i not in STATE_FIPS_REMOVE]


def get_state_data(state_fips):
    geo = censusdata.censusgeo(
        [
            ("state", str(state_fips).zfill(2)),
            ("county", "*"),
            ("tract", "*"),
            ("block", "*"),
        ]
    )
    return censusdata.download(
        "sf1", 2010, geo, ["STATE", "COUNTY", "TRACT", "BLOCK", "P001001"],
    )


for i in all_state_fips:
    print("Loading state %s" % i)
    l.append(get_state_data(i))

all_blocks = pd.concat(l)

all_blocks.to_csv("data/raw/census_block.csv.gz", index=False, compression="gzip")
