import os
import datetime

from predicu import load_all_data

datetimestr = datetime.datetime.now().strftime('%Y-%m-%d_%Hh%M')
filename = 'predicu_data_clean_{}.csv'.format(datetimestr)
path = os.path.join('/tmp', filename)
d = load_all_data()
d.to_csv(path)
