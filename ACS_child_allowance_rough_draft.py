import numpy as np
import pandas as pd
import microdf as mdf

raw = pd.read_stata("spm_2018_pu.dta")  # TODO: specify usecols
print(raw.columns.values)

# VAR LIST: 'spm_id' 'spm_capwkccxpns' 'spm_povthreshold' 'spm_resources' 'spm_poor'
# 'sporder' 'puma' 'age' 'hispanic' 'race' 'st' 'spm_numper'
# 'spm_numadults' 'spm_numkids' 'spm_totval' 'spm_fica' 'spm_fedtax'
# 'spm_fedtax\bc' 'spm_sttax' 'spm_wkxpns' 'spm_eitc' 'spm_wcohabit'
# 'spm_snapsub' 'spm_engval' 'spm_childcarexpns' 'spm_wicval'
# 'spm_schlunch' 'spm_tenmortstatus' 'spm_geoadj' 'spm_equivscale'
# 'spm_caphousesub' 'offpoor' 'wt' 'serialno' 'mar' 'education' 'sex'
# 'spm_wui_lt15' 'spm_medxpns'

person = raw
person["child"] = np.where(person["age"] < 18, 1, 0)
spmu = (
    person.groupby(["spm_id", "spm_resources"])[["child"]].sum().reset_index()
)
spmu.rename(columns={"child": "spmu_children"}, inplace=True)
spmu["new_resources"] = spmu["spm_resources"] + 1200 * spmu["spmu_children"]
person3 = person.merge(spmu[["new_resources", "spm_id"]], on=["spm_id"])
mdf.poverty_rate(person3, "new_resources", "spm_povthreshold", "wt")
mdf.poverty_rate(person3, "spm_resources", "spm_povthreshold", "wt")
just_children = person3[(person3.child == 1)]
mdf.poverty_rate(just_children, "new_resources", "spm_povthreshold", "wt")
mdf.poverty_rate(just_children, "spm_resources", "spm_povthreshold", "wt")

# Columns for PUMA, child, adult, or all, deep or regular, baseline and reform
def pov(data):
    base = mdf.poverty_rate(data, "spm_resources", "spm_povthreshold")
    reform = mdf.poverty_rate(data, "new_resources", "spm_povthreshold")
    deep_base = mdf.deep_poverty_rate(data, "spm_resources", "spm_povthreshold")
    deep_reform = mdf.deep_poverty_rate(data, "new_resources", "spm_povthreshold")
    return pd.Series(
        {
            "poverty_base": base,
            "poverty_reform": reform,
            "deep_poverty_base": deep_base,
            "deep_poverty_reform": deep_reform,
        }
    )

person3.groupby(["puma", "child"]).apply(pov)
# TODO: Add another not grouped by child
# Add pct change columns for poverty and deep poverty
# Stack those

# TODO:
# - Export to csv (data/poverty.csv)
# - import plotly.express as px; px.hist
