import json
import shutil

import predicu.data

d = predicu.data.load_data_file(predicu.data.DATA_PATHS["icubam"])

icu_name_to_department = dict(
    d[["icu_name", "icu_dept"]].itertuples(name=None, index=False)
)

shutil.copy(
    predicu.data.DATA_PATHS["icu_name_to_department"],
    "__backup__" + predicu.data.DATA_PATHS["icu_name_to_department"],
)

with open(predicu.data.DATA_PATHS["icu_name_to_department"], "w") as f:
    json.dump(icu_name_to_department, f)

d = load_all_data()
