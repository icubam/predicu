# predicu

Shared data wrangling and analysis code for the PredICU-COVID-19 effort team

## Install

```
git clone git@github.com:icubam/predicu.git
cd predicu
pip install -e .
```

## Usage

### Loading data

When loading data, file extensions should be either `.csv`, `.h5` or `.pickle`.

#### Load ICUBAM bedcount data (starting March 25th)

File extensions should be either `.csv`, `.h5` or `.pickle`.

```python
from predicu.data import load_icubam_bedcount_data

d = load_icubam_bedcount_data('bedcount_2020-03-31_14h54.{csv,h5,pickle}')
```

#### Load Antoine's pre-ICUBAM data (starting March 18th, ending March 25th)

```python
from predicu.data import load_pre_icubam_data

d = load_pre_icubam_data('my_data_file.{csv,h5,pickle}')
```

#### Load all data

```python
from predicu.data import load_all_data

d = load_all_data(
  icubam_bedcount_path='bedcount_2020-03-31_17h43.{csv,h5,pickle}',
  pre_icubam_path='my_data_file.{csv,h5,pickle}',
)
```
