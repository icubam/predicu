from predicu.data import load_icubam_bedcount_data, load_pre_icubam_data

pre_icubam_path = 'data/pre_icubam_data.csv'
old = load_pre_icubam_data(pre_icubam_path)
icubam_bedcount_path = 'data/bedcount_2020-03-31.pickle'
new = load_icubam_bedcount_data(icubam_bedcount_path)

old_icu_names = set(old.icu_name.unique())
new_icu_names = set(new.icu_name.unique())

print('icu_name in old data but not in new data')
print('-' * 30)
for icu_name in (old_icu_names - new_icu_names):
  print(icu_name)
print('-' * 30)
print('icu_name in old data but not in new data')
print('-' * 30)
for icu_name in (new_icu_names - old_icu_names):
  print(icu_name)
