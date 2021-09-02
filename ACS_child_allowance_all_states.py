import numpy as np
import pandas as pd
import microdf as mdf
from pandas.core.reshape.concat import concat
import requests
import plotly.graph_objects as go
import plotly.figure_factory as ff

url = "https://raw.githubusercontent.com/UBICenter/local-child-allowance/main/data/puma_upper_lower_leg_district.csv"
res = requests.get(url, allow_redirects=True)
with open("puma_upper_lower_leg_district.csv", "wb") as file:
    file.write(res.content)
puma_upper_lower_leg_district = pd.read_csv("puma_upper_lower_leg_district.csv")

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


person = pd.concat(years_frame)

puma_upper_lower_leg_district.puma = puma_upper_lower_leg_district.puma.astype(int)
puma_upper_lower_leg_district.puma = puma_upper_lower_leg_district.puma.astype(
    str
).str.zfill(5)
puma_upper_lower_leg_district["state_puma"] = (
    puma_upper_lower_leg_district["state_fip"].astype(str)
    + puma_upper_lower_leg_district["puma"]
)
person.rename(columns={"puma": "state_puma"}, inplace=True)
# DC and collection error
person_clean = person[(person.st != 11) & (person.st != 99)]
person_clean["child"] = np.where(person_clean["age"] < 18, 1, 0)
spmu = (
    person_clean.groupby(["spm_id", "spm_resources", "year"])[["child"]]
    .sum()
    .reset_index()
)
spmu.rename(columns={"child": "spmu_children"}, inplace=True)
ANNUAL_CHILD_ALLOWANCE = 1200
spmu["new_resources"] = spmu.spm_resources + ANNUAL_CHILD_ALLOWANCE * spmu.spmu_children
person_clean3 = person_clean.merge(
    spmu[["spm_id", "new_resources", "year"]], on=["year", "spm_id"]
)
pov_by_state = person_clean3.groupby(["st"]).apply(pov).reset_index()
pov_by_state["pct_chg"] = pct_chg(pov_by_state)
pov_by_state["pct_chg_deep"] = pct_chg_deep(pov_by_state)
state_names = pd.read_csv("us_state_fips.csv")
state_names.columns
state_names.rename(columns={" st": "st", " stusps": "stusps",}, inplace=True)
person_clean3.rename(columns={"puma": "state_puma"}, inplace=True)
person_clean3_kids = person_clean3[(person_clean3.child == 1)]
person_clean3_CA = person_clean3[(person_clean3.st == 6)]
person_clean3_CA_kids = person_clean3_CA[(person_clean3.child == 1)]
person_clean3.state_puma = person_clean3.state_puma.astype(int)
person_clean3.state_puma = person_clean3.state_puma.astype(str)
puma_upper_lower_leg_district.state_puma = puma_upper_lower_leg_district.state_puma.astype(
    int
)
person_merged = puma_upper_lower_leg_district.merge(person_clean3, on="state_puma")
person_merged.wt *= person_merged.share_of_puma_pop
person_merged_only_children = person_merged[(person_merged.child == 1)]
pov_by_lower_leg_district = (
    person_merged.groupby(["st", "lower_leg_district"]).apply(pov).reset_index()
)
pov_by_lower_leg_district_children = (
    person_merged_only_children.groupby(["st", "lower_leg_district"])
    .apply(pov)
    .reset_index()
)
pov_by_upper_leg_district = (
    person_merged.groupby(["st", "upper_leg_district"]).apply(pov).reset_index()
)
pov_by_upper_leg_district_children = (
    person_merged_only_children.groupby(["st", "upper_leg_district"])
    .apply(pov)
    .reset_index()
)
pov_by_lower_leg_district["pct_chg"] = pct_chg(pov_by_lower_leg_district)
pov_by_lower_leg_district["pct_chg_deep"] = pct_chg_deep(pov_by_lower_leg_district)
pov_by_lower_leg_district_children["pct_chg"] = pct_chg(
    pov_by_lower_leg_district_children
)
pov_by_lower_leg_district_children["pct_chg_deep"] = pct_chg_deep(
    pov_by_lower_leg_district_children
)
pov_by_upper_leg_district["pct_chg"] = pct_chg(pov_by_upper_leg_district)
pov_by_upper_leg_district["pct_chg_deep"] = pct_chg_deep(pov_by_upper_leg_district)
pov_by_upper_leg_district_children["pct_chg"] = pct_chg(
    pov_by_upper_leg_district_children
)
pov_by_upper_leg_district_children["pct_chg_deep"] = pct_chg_deep(
    pov_by_upper_leg_district_children
)
pov_by_lower_leg_district_children.columns = [
    "child_" + i for i in pov_by_lower_leg_district_children.columns
]
pov_by_upper_leg_district_children.columns = [
    "child_" + i for i in pov_by_upper_leg_district_children.columns
]
pov_by_lower_leg_district_children.rename(
    columns={"child_lower_leg_district": "lower_leg_district", "child_st": "st"},
    inplace=True,
)
pov_by_upper_leg_district_children.rename(
    columns={"child_upper_leg_district": "upper_leg_district", "child_st": "st"},
    inplace=True,
)
pov_by_lower_leg_district_children
pov_by_lower_leg_district
pov_all_lower_leg_district = pov_by_lower_leg_district.merge(
    pov_by_lower_leg_district_children, on=["st", "lower_leg_district"]
)
pov_all_upper_leg_district = pov_by_upper_leg_district.merge(
    pov_by_upper_leg_district_children, on=["st", "upper_leg_district"]
)
pov_all_lower_leg_district.to_csv(r"pov_all_lower_leg_district.csv")
pov_all_upper_leg_district.to_csv(r"pov_all_upper_leg_district.csv")
