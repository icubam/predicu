import argparse
import os

import matplotlib.cm
import matplotlib.gridspec
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import pandas as pd

from predicu.data import CUM_COLUMNS, NCUM_COLUMNS, load_all_data

COLUMN_TO_HUMAN_READABLE = {
  "n_covid_deaths": "décès",
  "n_covid_healed": "sorties",
  "n_covid_transfered": "transferts",
  "n_covid_refused": "refusé",
  "n_covid_free": "lits Covid+ libres",
  "n_ncovid_free": "lits Covid- libres",
  "n_covid_occ": "lits Covid+ occupés",
  "n_ncovid_occ": "lits Covid- occupés",
}

COLUMN_COLOR = {
  col: matplotlib.cm.Set2(i)
  for i, col in enumerate(sorted(set(CUM_COLUMNS) | set(NCUM_COLUMNS)))
}


def plot_icu_values(icu_name, data_clean, path, data_raw):
  all_dates = sorted(list(data_clean.date.unique()))
  fig = plt.figure(figsize=(18, 10))
  gs = matplotlib.gridspec.GridSpec(2, 2)
  ax_c_raw = fig.add_subplot(gs[0, 0])
  ax_c_raw.set_title('Valeurs cumulées avant traitement')
  ax_c_clean = fig.add_subplot(gs[0, 1], sharey=ax_c_raw)
  ax_c_clean.set_title('Valeurs cumulées après traitement')
  ax_nc_raw = fig.add_subplot(gs[1, 0])
  ax_nc_raw.set_title('Valeurs non-cumulées avant traitement')
  ax_nc_clean = fig.add_subplot(gs[1, 1], sharey=ax_nc_raw)
  ax_nc_clean.set_title('Valeurs non-cumulées après traitement')
  data_clean = data_clean.set_index('datetime').sort_index()
  data_raw = data_raw.loc[data_raw.icu_name == icu_name
                          ].set_index('datetime').sort_index()
  for i, (cols_grp, ax_raw,
          ax_clean) in enumerate([(CUM_COLUMNS, ax_c_raw, ax_c_clean),
                                  (NCUM_COLUMNS, ax_nc_raw, ax_nc_clean)]):
    for col in cols_grp:
      for j, (ax, df) in enumerate(
        [(ax_raw, data_raw), (ax_clean, data_clean)]
      ):
        ax.plot(
          df.index,
          df[col],
          # df[col].cumsum() if (i == 0 and j == 1) else df[col],
          label=COLUMN_TO_HUMAN_READABLE[col],
          color=COLUMN_COLOR[col]
        )
    for ax, data in [(ax_raw, data_raw), (ax_clean, data_clean)]:
      ax.legend(ncol=2, loc="upper left", frameon=True)
      ax.set_xticks(all_dates)
      ax.set_xticklabels([date.strftime('%d/%m') for date in all_dates],
                         rotation=45,
                         fontdict={'fontsize': 'x-small'})
  fig.suptitle(icu_name)
  fig.tight_layout()
  fig.savefig(path)


def main(output_dir):
  if not os.path.isdir(output_dir):
    print('creating directory', output_dir)
    os.makedirs(output_dir)
  data_raw = load_all_data(clean=False)
  data_clean = load_all_data()
  for icu_name, dg in data_clean.groupby('icu_name'):
    path = os.path.join(output_dir, '{}.pdf'.format(icu_name))
    plot_icu_values(icu_name, dg, path, data_raw)


if __name__ == "__main__":
  matplotlib.style.use('seaborn-whitegrid')
  parser = argparse.ArgumentParser()
  parser.add_argument('--output-dir', default='/tmp/plot_per_icu_values')
  args = parser.parse_args()
  main(args.output_dir)
