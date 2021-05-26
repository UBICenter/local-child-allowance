import numpy as np
import pandas as pd
import microdf as mdf

person = pd.read_stata(
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
print(raw.columns.values)

# VAR LIST: 'spm_id' 'spm_povthreshold' 'spm_resources'
#  'puma' 'age' 'st' 'spm_totval' 'wt'

mapping_house = pd.read_csv(
    "Mapping1.csv",
    usecols=["Assembly District Number", "PUMA Description", "STATEFIP", "PUMA"],
)
mapping_senate = pd.read_csv(
    "Mapping2.csv", usecols=["Senate District Number", "PUMA", "STATEFIP"]
)
mapping_senate
mapping_house
mapping_senate["Senate District Number"].nunique()
mapping_senate_CA = mapping_senate[(mapping_senate["STATEFIP"] == 6)]
mapping_house_CA = mapping_house[(mapping_house["STATEFIP"] == 6)]
mapping_merged_CA = mapping_house_CA.merge(
    mapping_senate_CA[["Senate District Number", "PUMA"]], on=["PUMA"]
)
mapping_merged_CA = mapping_merged_CA.rename(columns={"PUMA": "puma"})
mapping_merged_CA

person["child"] = np.where(person["age"] < 18, 1, 0)
spmu = person.groupby(["spm_id", "spm_resources"])[["child"]].sum().reset_index()
spmu.rename(columns={"child": "spmu_children"}, inplace=True)
ANNUAL_CHILD_ALLOWANCE = 1200
spmu["new_resources"] = spmu.spm_resources + ANNUAL_CHILD_ALLOWANCE * spmu.spmu_children
person3 = person.merge(spmu[["new_resources", "spm_id"]], on=["spm_id"])
mdf.poverty_rate(person3, "new_resources", "spm_povthreshold", "wt")
mdf.poverty_rate(person3, "spm_resources", "spm_povthreshold", "wt")
just_children = person3[(person3.child == 1)]
mdf.poverty_rate(just_children, "new_resources", "spm_povthreshold", "wt")
mdf.poverty_rate(just_children, "spm_resources", "spm_povthreshold", "wt")
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


grouped_puma_child = person3.groupby(["puma", "child"]).apply(pov).reset_index()
grouped_puma = person3.groupby(["puma"]).apply(pov).reset_index()
grouped_puma
grouped_puma_child["pct_change"] = (
    grouped_puma_child["poverty_base"] - grouped_puma_child["poverty_reform"]
) / grouped_puma_child["poverty_base"]
grouped_puma_child["pct_change_deep"] = (
    grouped_puma_child["deep_poverty_base"] - grouped_puma_child["deep_poverty_reform"]
) / grouped_puma_child["deep_poverty_base"]
grouped_puma["pct_change"] = (
    grouped_puma["poverty_base"] - grouped_puma["poverty_reform"]
) / grouped_puma["poverty_base"]
grouped_puma["pct_change_deep"] = (
    grouped_puma_child["deep_poverty_base"] - grouped_puma_child["deep_poverty_reform"]
) / grouped_puma_child["deep_poverty_base"]
grouped_list = [grouped_puma, grouped_puma_child]
grouped_df = pd.concat(grouped_list).reset_index()
only_children_pumas = grouped_puma_child[(grouped_puma_child.child == 1)]
grouped_puma_no_change = grouped_puma[(grouped_puma["pct_change"] == 0)]
grouped_df.to_csv(r"spm_by_puma.csv")
import plotly.express as px

px.histogram(grouped_df["pct_change"])
px.histogram(grouped_df["pct_change_deep"])

# About 13% of PUMAs have no change in the poverty rate

### Just California
CA_FIPS = 6
just_california = person3[(person3.st == CA_FIPS)].reset_index()
just_california_children = just_california[(just_california.child == 1)].reset_index()
# by individual
poverty_change_CA = pov(just_california)
poverty_change_CA_children = pov(just_california_children)
poverty_change_CA_children
just_california["puma"] = just_california["puma"].astype(int)
just_california["puma"]
just_california["puma"] = just_california.puma - 600000
just_california["puma"]
merged_individuals_CA = just_california.merge(
    mapping_merged_CA[
        [
            "PUMA Description",
            "puma",
            "Assembly District Number",
            "Senate District Number",
        ]
    ],
    on=["puma"],
)
pov(merged_individuals_CA)
poverty_change_CA
merged_individuals_CA.puma.nunique()
just_california.puma.nunique()
# Difference likely from four missing pumas
pov_by_assembly = (
    merged_individuals_CA.groupby(["Assembly District Number",])
    .apply(pov)
    .reset_index()
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
pov_by_assembly_children
pov_by_senate_children
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
pov_by_senate_children = pov_by_senate_children[(pov_by_senate_children.child == 1)]
pov_by_senate.to_csv(r"pov_by_senate_CA.csv")
pov_by_senate_children.to_csv(r"pov_by_senate_children_CA.csv")
pov_by_assembly.to_csv(r"pov_by_assembly_CA.csv")
pov_by_assembly_children.to_csv(r"pov_by_assembly_children_CA.csv")
