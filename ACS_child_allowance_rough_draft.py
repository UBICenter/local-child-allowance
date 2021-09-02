import numpy as np
import pandas as pd
import microdf as mdf
from pandas.core.reshape.concat import concat

person2018 = pd.read_stata(
    "spm_2018_pu.dta",
    columns=[
        "spm_id",
        "puma",
        "spm_povthreshold",
        "spm_resources",
        "age",
        "spm_totval",
        "st",
        "wt",
    ],
)
person2018["year"] = 2018
person2017 = pd.read_stata(
    "spm_2017_pu.dta",
    columns=[
        "spm_id",
        "puma",
        "spm_povthreshold",
        "spm_resources",
        "age",
        "spm_totval",
        "st",
        "wt",
    ],
)
person2017["year"] = 2017
person2016 = pd.read_stata(
    "spm_2016_pu.dta",
    columns=[
        "spm_id",
        "puma",
        "spm_povthreshold",
        "spm_resources",
        "age",
        "spm_totval",
        "st",
        "wt",
    ],
)
person2016["year"] = 2016
years_frame = [person2018, person2017, person2016]
person = pd.concat(years_frame)
# VAR LIST: 'spm_id' 'spm_povthreshold' 'spm_resources'
#  'puma' 'age' 'st' 'spm_totval' 'wt'
mapping_house = pd.read_csv(
    "Mapping1.csv",
    usecols=["Assembly District Number", "PUMA Description", "STATEFIP", "PUMA"],
)
mapping_senate = pd.read_csv(
    "Mapping2.csv", usecols=["Senate District Number", "PUMA", "STATEFIP"]
)

mapping_merged = mapping_house.merge(
    mapping_senate[["Senate District Number", "PUMA", "STATEFIP"]],
    on=["STATEFIP", "PUMA"],
)
mapping_merged = mapping_merged.rename(columns={"PUMA": "puma"})

person["child"] = np.where(person["age"] < 18, 1, 0)
spmu = (
    person.groupby(["spm_id", "spm_resources", "year"])[["child"]].sum().reset_index()
)
spmu.rename(columns={"child": "spmu_children"}, inplace=True)
ANNUAL_CHILD_ALLOWANCE = 1200
spmu["new_resources"] = spmu.spm_resources + ANNUAL_CHILD_ALLOWANCE * spmu.spmu_children
person3 = person.merge(spmu[["spm_id", "new_resources", "year"]], on=["year", "spm_id"])
person3.new_resources.describe()
person3.spm_resources.describe()

just_children = person3[(person3.child == 1)]
# Columns for PUMA, child, adult, or all, deep or regular, baseline and reform


def pov(data):
    base = mdf.poverty_rate(data, "spm_resources", "spm_povthreshold", "wt")
    reform = mdf.poverty_rate(data, "new_resources", "spm_povthreshold", "wt")
    deep_base = mdf.deep_poverty_rate(data, "spm_resources", "spm_povthreshold", "wt")
    deep_reform = mdf.deep_poverty_rate(data, "new_resources", "spm_povthreshold", "wt")
    return pd.Series(
        {
            "poverty_base": base,
            "poverty_reform": reform,
            "deep_poverty_base": deep_base,
            "deep_poverty_reform": deep_reform,
        }
    )


def pct_chg(data):
    return (data["poverty_base"] - data["poverty_reform"]) / data["poverty_base"]


def pct_chg_deep(data):
    return (data["deep_poverty_base"] - data["deep_poverty_reform"]) / data[
        "deep_poverty_base"
    ]


grouped_puma_child = person3.groupby(["puma", "child"]).apply(pov).reset_index()
grouped_puma = person3.groupby(["puma"]).apply(pov).reset_index()
grouped_puma_child["pct_change"] = pct_chg(grouped_puma_child)
grouped_puma_child["pct_change_deep"] = pct_chg_deep(grouped_puma_child)
grouped_puma["pct_change"] = pct_chg(grouped_puma)
grouped_puma["pct_change_deep"] = pct_chg_deep(grouped_puma)
grouped_list = [grouped_puma, grouped_puma_child]
grouped_df = pd.concat(grouped_list).reset_index()
only_children_pumas = grouped_puma_child[(grouped_puma_child.child == 1)]
grouped_puma_no_change = grouped_puma[(grouped_puma["pct_change"] == 0)]
grouped_df.to_csv(r"spm_by_puma.csv")
import plotly.express as px

px.histogram(grouped_df["pct_change"])
px.histogram(grouped_df["pct_change_deep"])

# About 13% of PUMAs have no change in the poverty rate
### Find pov by state


### Just California
CA_FIPS = 6
just_california = person3[(person3.st == CA_FIPS)].reset_index()
just_california_children = just_california[(just_california.child == 1)].reset_index()
# by individual
poverty_change_CA = pov(just_california)
poverty_change_CA
poverty_change_CA_children = pov(just_california_children)
poverty_change_CA_pct = pct_chg(poverty_change_CA)
poverty_change_CA_pct
poverty_change_CA_children_pct = pct_chg(poverty_change_CA_children)
poverty_change_CA_children_pct
just_california["puma"] = just_california["puma"].astype(int)
just_california["puma"] = just_california.puma - 600000
just_california["puma"]
mapping_CA = mapping_merged[(mapping_merged.STATEFIP == 6)]
merged_individuals_CA = just_california.merge(
    mapping_CA[
        [
            "PUMA Description",
            "puma",
            "Assembly District Number",
            "Senate District Number",
        ]
    ],
    on=["puma"],
)
# Difference likely from four missing pumas
pov_by_assembly = (
    merged_individuals_CA.groupby(["Assembly District Number"]).apply(pov).reset_index()
)
pov_by_assembly_children = (
    merged_individuals_CA.groupby(["Assembly District Number", "child"])
    .apply(pov)
    .reset_index()
)
pov_by_senate = (
    merged_individuals_CA.groupby(["Senate District Number"]).apply(pov).reset_index()
)
pov_by_senate_children = (
    merged_individuals_CA.groupby(["Senate District Number", "child"])
    .apply(pov)
    .reset_index()
)
pov_by_assembly
pov_by_assembly["pct_change"] = (
    pov_by_assembly["poverty_base"] - pov_by_assembly["poverty_reform"]
) / pov_by_assembly["poverty_base"]
pov_by_assembly["pct_change_deep"] = (
    pov_by_assembly["deep_poverty_base"] - pov_by_assembly["deep_poverty_reform"]
) / pov_by_assembly["deep_poverty_base"]
pov_by_assembly_children["pct_change"] = (
    pov_by_assembly_children["poverty_base"]
    - pov_by_assembly_children["poverty_reform"]
) / pov_by_assembly_children["poverty_base"]
pov_by_assembly_children["pct_change_deep"] = (
    pov_by_assembly_children["deep_poverty_base"]
    - pov_by_assembly_children["deep_poverty_reform"]
) / pov_by_assembly_children["deep_poverty_base"]
pov_by_assembly_only_children = pov_by_assembly_children[
    (pov_by_assembly_children.child == 1)
]
pov_by_senate["pct_change"] = (
    pov_by_senate["poverty_base"] - pov_by_senate["poverty_reform"]
) / pov_by_senate["poverty_base"]
pov_by_senate["pct_change_deep"] = (
    pov_by_senate["deep_poverty_base"] - pov_by_senate["deep_poverty_reform"]
) / pov_by_senate["deep_poverty_base"]
pov_by_senate_children["pct_change"] = (
    pov_by_senate_children["poverty_base"] - pov_by_senate_children["poverty_reform"]
) / pov_by_senate_children["poverty_base"]
pov_by_senate_children["pct_change_deep"] = (
    pov_by_senate_children["deep_poverty_base"]
    - pov_by_senate_children["deep_poverty_reform"]
) / pov_by_senate_children["deep_poverty_base"]
pov_by_senate_only_children = pov_by_senate_children[
    (pov_by_senate_children.child == 1)
]
pov_by_assembly_only_children.columns = [
    "child_" + i for i in pov_by_assembly_children.columns
]
pov_by_senate_only_children.columns = [
    "child_" + i for i in pov_by_senate_only_children.columns
]
pov_by_senate_only_children.describe()
pov_by_assembly_only_children.rename(
    columns={"child_Assembly District Number": "Assembly District Number"}, inplace=True
)
pov_by_senate_only_children.rename(
    columns={"child_Senate District Number": "Senate District Number"}, inplace=True
)
pov_by_senate_only_children.describe()
pov_all_assembly = pov_by_assembly.merge(
    pov_by_assembly_only_children, on="Assembly District Number"
)
pov_all_senate = pov_by_senate.merge(
    pov_by_senate_only_children, on="Senate District Number"
)


pov_all_senate.to_csv(r"pov_all_senate_2.csv")
pov_by_senate_children.to_csv(r"pov_by_senate_children_CA.csv")
pov_all_assembly.to_csv(r"pov_all_assembly_2.csv")
