import matplotlib.cm

from predicu.data import CUM_COLUMNS, NCUM_COLUMNS

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
