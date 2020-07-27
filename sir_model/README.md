# **`ICUBAM`: ICU Bed Availability Monitoring and analysis in the *Grand Est région* of France during the COVID-19 epidemic.**
### https://doi.org/10.1101/2020.05.18.20091264
# Python source code for SIR-like modeling
by Laurent Bonnasse-Gahot & Jean-Pierre Nadal

See Section IV.1 and Appendix F of the paper.

---
## How to get the data
Download data (provided you have access to a proper API key) at the following url:
`https://prod.icubam.net/db/all_bedcounts?API_KEY=<API_KEY>&preprocess=true&format=csv`
This file should be placed in the `data/` folder.

## Code organization
The project is organized with the following structure:

```
├── model_icubam.py
├── model_icubam_ml_fit.ipynb
├── model_icubam_ml_plot.ipynb
├── model_icubam_cr_sample.ipynb
├── model_icubam_cr_plot.ipynb
├── data/
├── fig/
└── model/
    ├── samples/
    └── params_hat.csv
```
The location of each of these folders can be changed in the `model_icubam.py` file. This file also contains the code for running the SIR like model.

The data folder includes the pop_dep_2020.csv file that contains the population size of each French département (population as of Jan, 2020). Source: [INSEE](https://www.insee.fr/fr/statistiques/4265429).

## Dependencies

Computation of the credible regions makes use of the [PyMC3](https://docs.pymc.io/) package.

See requirements.txt for the full list of packages used in this work. This file provides the exact version that was used, but the code is expected to work with other versions as well.

## Run the notebooks

Launch `jupyter-notebook` and open the following notebooks:

(i) [model_icubam_ml_fit.ipynb](model_icubam_ml_fit.ipynb):
compute model, fit to the data, and save best parameters found via maximum likelihood

(ii) [model_icubam_ml_plot.ipynb](model_icubam_ml_plot.ipynb):
 visualize results from maximum likelihood estimation, reproducing Fig. 17(left) of the paper

(iii) [model_icubam_cr_sample.ipynb](model_icubam_cr_sample.ipynb):
compute and save samples from the posterior distribution P(parameters|data)

(iv) [model_icubam_cr_plot.ipynb](model_icubam_cr_plot.ipynb):
visualize results with credible regions, reproducing Fig. 11 and Fig. 17(right) of the paper
