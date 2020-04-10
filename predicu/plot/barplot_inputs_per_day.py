import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import pandas as pd
import seaborn as sns

import predicu.data

data_source = "icubam_data"

def plot(icubam_data=None, api_key=None):
    if icubam_data is not None:
        d = icubam_data
    else:
        d = predicu.data.load_icubam_data(api_key=api_key)
    d = d.rename(columns={"create_date": "date"})
    d = predicu.data.format_data(d, predicu.data.load_icu_name_to_department())
    counts = d.groupby(["date", "icu_name"]).datetime.count().values
    fig, ax = plt.subplots(1, figsize=(12, 8))
    sns.countplot(counts)
    # ax.set_title('Distributions des nombres de saisies par date et par ICU')
    ax.set_xlabel("Nombre de saisies dans la journée")
    ax.set_ylabel("Compte par date et réanimation")
    return fig, dict()
