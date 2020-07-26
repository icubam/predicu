# predicu

Shared data wrangling and analysis code for the PredICU-COVID-19 effort team

## Install

```
git clone git@github.com:icubam/predicu.git
cd predicu
pip install -e .
```

## Usage

### Pre-process and export data

```
python -m predicu export --output-dir <path> --api-key <key> --max-date <date>
```


### Generate all the plots

```
python -m predicu.plot \
    --output-dir <path> \
    --api-key <key> \
    --matplotlib-style <style> \
    --plots [PLOT [PLOT ...]] \
    --output-type {tex,png,pdf}
```

## SIR model

This repository also contains a SIR like model used in the ICUBAM paper. See
[./sir_model/README.md](./sir_model/README.md) for more details.
