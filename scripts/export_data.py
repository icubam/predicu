import datetime
import os

import predicu.data

datetimestr = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%M")
filename = "predicu_data_clean_{}.csv".format(datetimestr)
path = os.path.join("/tmp", filename)
d = predicu.data.load_all_data(clean=True, cache=False)
d.to_csv(path)
