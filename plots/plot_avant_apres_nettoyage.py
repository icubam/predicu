import numpy as np
import pandas as pd
import os
import time

import matplotlib.gridspec
import matplotlib.pyplot as plt
import matplotlib.style
#import seaborn as sns

# from predicu.data import load_all_data
# from predicu.data import get_clean_daily_values
# from predicu.data import load_icubam_data
import predicu.data

matplotlib.style.use('seaborn-whitegrid')

# icubam_bedcount_path = '~/Documents/Thèse/Covid/bedcount_2020-03-31.csv'
# pre_icubam_path = '~/Documents/Thèse/Covid/Grand_Est_df.csv'
icubam_bedcount_path = 'data/bedcount_2020-03-31.pickle'
pre_icubam_path = 'data/pre_icubam_data.csv'

## pre-ICUbam: clean a la main par Antoine, il me semble ?
# data = predicu.data.load_all_data(
#   icubam_bedcount_path=icubam_bedcount_path, pre_icubam_path=pre_icubam_path
# )
# cleanData = predicu.data.get_clean_daily_values(data)
def pd_2_np(bc):
    bc.sort_values(by=['icu_name', 'date'], inplace = True)
    ICUs = bc["icu_name"]
    n_covid_occ= np.array(bc["n_covid_occ"])   # n_covid_occ: nombre de lits de réanimation équipés d'un respirateur occupés
    n_covid_free= np.array(bc["n_covid_free"])   # n_covid_free: nombre de lits de réanimation équipés d'un respirateur libres
    n_ncovid_free= np.array(bc["n_ncovid_free"])   # n_ncovid_free: nombre de lits de réanimation équipés sans respirateur libres
    n_covid_deaths= np.array(bc["n_covid_deaths"])   # n_covid_deaths: nombre de morts liés au COVID (cumulé)
    n_covid_healed= np.array(bc["n_covid_healed"])   # n_covid_healed: nombre de guerisson (sortie d'hopital) liés au COVID (cumulé)
    n_covid_refused= np.array(bc["n_covid_refused"])   # n_covid_refused: nombre d'admission refusés de COVID (cumulé)
    n_covid_transfered= np.array(bc["n_covid_transfered"]) # transferts (cumulé)
    datetimes = np.array(bc["datetime"])
    dates_timestamps = np.array(bc["date"])
    np_values_7_cols = np.array(  [n_covid_occ, n_covid_free, n_ncovid_free, n_covid_deaths, n_covid_healed, n_covid_refused, n_covid_transfered])

    np_bc = [ICUs, datetimes, np_values_7_cols] # equivalent of pandas data series but in lists/numpy
    # dates_timestamps -> ?
    return np_bc

# numpy 2 pandas
def np_2_pd(np_bc):
    ICUs = np_bc[0]
    datetimes = np_bc[1]
    np_values_7_cols = np_bc[2]
    n_covid_occ, n_covid_free, n_ncovid_free, n_covid_deaths, n_covid_healed, n_covid_refused, n_covid_transfered = np_values_7_cols

    Ndata = n_covid_occ.shape[0]

    pandas_frame = list()
    start=0
    aux_icu=0
    for icu_num, icu in enumerate(ICUs.unique()):
        ## remarque: le re-ordonancement n'est pas reellement necessaire
        start+=aux_icu
        aux_icu=0
        ICUrange = np.arange(Ndata)[np.array(icu == ICUs)] ## array des indices (absolus, pour pouvoir corriger) de cet ICU
        sorting = np.argsort(datetimes[ICUrange])   ## indice interne de l'ordre chronologique
        ICUrange = ICUrange[sorting] ## range des indices de cet ICU ds le bon ordre
        for i, date in enumerate(datetimes[ICUrange]):
            new_data_point = {'datetime': date,\
                                'date': date, \
                                'icu_name': icu, \
                                'n_covid_occ' : n_covid_occ[start+i], \
                                'n_covid_free' : n_covid_free[start+i], \
                                'n_ncovid_free' : n_ncovid_free[start+i], \
                                'n_covid_deaths' : n_covid_deaths[start+i], \
                                'n_covid_healed' : n_covid_healed[start+i], \
                                'n_covid_refused' : n_covid_refused[start+i], \
                                'n_covid_transfered' : n_covid_transfered[start+i]}
            pandas_frame.append(new_data_point)
            aux_icu+=1
    return pd.DataFrame(pandas_frame)



# plots avant/apres pour validation facile (visuelle, idealement en faisant defiler
# des .png depuis un visionneur d'images) par un expert (medecin)
def plot_compare_2_dataBases(bc_origin, bc_corrected,plot_also_instant_values=True, suffixe=""):
    pathname="figs-"+suffixe
    if not os.path.exists(pathname):
        os.makedirs(pathname)

    columnNames = ["n_covid_occ", "n_covid_free", "n_ncovid_free", "n_covid_deaths", "n_covid_healed", "n_covid_refused", "n_covid_transfered"]
    columnNamesFR = ["lits covid+ occupes", "lits covid+ libres", "lits non covid libres", "deces covid", "sorties covid", "refusés", "transférés"]

    # T0 = np.min(datetimes) # premier record (jour)
    T0 = np.datetime64('2020-03-17T00:00:00.000000000')
    times = np.array((bc_origin['datetime']-T0), dtype=float)/86400.0/1.e9
    timesCorr = np.array((bc_corrected['datetime']-T0), dtype=float)/86400.0/1.e9

    for icu_num, icu in enumerate(bc_origin["icu_name"].unique()):
        ICUmask = np.array(bc_origin["icu_name"] == icu)
        ICUmaskCorr = np.array(icu == bc_corrected["icu_name"])

        ## on ne plot rien si les 2 series sont identiques (mais attention aux re-ordonancements qui peuvent tromper)
        pandasSeriesAreEqual = False
        if (bc_origin[ICUmask]).equals(bc_corrected[ICUmaskCorr]):
            pandasSeriesAreEqual = True
        else:
            pandasSeriesAreEqual = True
            for col_num in range(0,7):
                colName = columnNames[col_num]
                if np.array_equal(bc_origin[colName][ICUmask] , bc_corrected[colName][ICUmaskCorr]) == False:
                    pandasSeriesAreEqual = False

        # if np.array_equal(bc_origin["n_covid_occ"], bc_corrected["n_covid_occ"] )==False:
        if pandasSeriesAreEqual == False :

            # if plot_also_instant_values :
            ## les 3 premiere scolonnes en sont pas changees ni validees, pour le moment
            ## plots des lits (valeurs non cumulatives)
            plt.figure(icu_num*2,[10,10])

            plt.title(icu+" données instantanées")

            ## before correction
            plt.subplot(2, 2, 1)
            plt.title(icu+ " avant correction")
            # n_respi_total =  bc_origin.loc[ICUmask,'n_covid_occ'] +  bc_origin.loc[ICUmask,'n_covid_free']
            # plt.plot(times[ICUmask], n_respi_total, label='total lits covid' , lw=2, marker='o')
            # for col_num in range(1,3):
            #     colName = columnNames[col_num]
            #     plt.plot(times[ICUmask],bc_origin[colName][ICUmask] , label=colName ,lw=2, marker='o')
            # plt.legend()
            n_entrants = bc_origin["n_covid_occ"][ICUmask] +bc_origin["n_covid_deaths"][ICUmask] +bc_origin["n_covid_healed"][ICUmask] +bc_origin["n_covid_transfered"][ICUmask]
            n_entrants = n_entrants.diff(1)
            n_demandants = bc_origin["n_covid_occ"][ICUmask] +bc_origin["n_covid_deaths"][ICUmask] +bc_origin["n_covid_healed"][ICUmask] +bc_origin["n_covid_transfered"][ICUmask]+bc_origin["n_covid_refused"][ICUmask]
            n_demandants = n_entrants.diff(1)
            plt.plot(times[ICUmask],bc_origin["n_covid_occ"][ICUmask] + bc_origin["n_covid_free"][ICUmask] , label='lits covid - total' , lw=2, marker='o', color= "green")
            plt.plot(times[ICUmask],bc_origin["n_covid_free"][ICUmask] , label="lits covid dispos" , lw=2, marker='o', color= "red")
            plt.plot(times[ICUmask],n_entrants             , label='total entrants' , lw=2, marker='o', color= "purple")
            plt.plot(times[ICUmask],n_demandants  , label="pression a l'entree" , lw=2, marker='o', color= "black")
            # for col_num in range(1,3):
            #     colName = columnNames[col_num]
            #     plt.plot(times[ICUmask],bc_origin[colName][ICUmask] , label=colName , lw=2, marker='o')
            plt.legend()
            plt.ylim([-5,40])
            plt.xlabel("jours (depuis 17 mars)") # depuis 17 mars


            ## after correction
            plt.subplot(2, 2, 2)
            plt.title(icu+ " apres correction")
            n_entrants = bc_corrected["n_covid_occ"][ICUmaskCorr] +bc_corrected["n_covid_deaths"][ICUmaskCorr] +bc_corrected["n_covid_healed"][ICUmaskCorr] +bc_corrected["n_covid_transfered"][ICUmaskCorr]
            n_entrants = n_entrants.diff(1)
            n_demandants = bc_corrected["n_covid_occ"][ICUmaskCorr] +bc_corrected["n_covid_deaths"][ICUmaskCorr] +bc_corrected["n_covid_healed"][ICUmaskCorr] +bc_corrected["n_covid_transfered"][ICUmaskCorr]+bc_corrected["n_covid_refused"][ICUmaskCorr]
            n_demandants = n_entrants.diff(1)
            plt.plot(timesCorr[ICUmaskCorr],bc_corrected["n_covid_occ"][ICUmaskCorr] + bc_corrected["n_covid_free"][ICUmaskCorr] , label='lits covid - total' , lw=2, marker='o', color= "green")
            plt.plot(timesCorr[ICUmaskCorr],bc_corrected["n_covid_free"][ICUmaskCorr] , label="lits covid dispos" , lw=2, marker='o', color= "red")
            plt.plot(timesCorr[ICUmaskCorr],n_entrants             , label='total entrants' , lw=2, marker='o', color= "purple")
            plt.plot(timesCorr[ICUmaskCorr],n_demandants  , label="pression a l'entree" , lw=2, marker='o', color= "black")
            plt.legend()
            plt.ylim([-5,40])
            plt.xlabel("jours (depuis 17 mars)") # depuis 17 mars

            # n_respi_total = bc_corrected["n_covid_occ"][ICUmaskCorr] + bc_corrected["n_covid_free"][ICUmaskCorr]
            # plt.plot(timesCorr[ICUmaskCorr], n_respi_total, label='total lits covid' , lw=2, marker='o')
            # for col_num in range(1,3):
            #     colName = columnNames[col_num]
            #     plt.plot(timesCorr[ICUmaskCorr],bc_corrected[colName][ICUmaskCorr] , label=colName ,lw=2, marker='o')
            # plt.legend()

            maxVals = np.zeros(4) # pour mettre le meme axe des y, pour fciliter la lecture
            ## plots des valeurs cumulatives
            color = ["b","b","b","black","green","red", "blue"]

            ## before correction
            plt.subplot(2, 2, 3)
            plt.title(icu+ " avant correction")
            for col_num in range(3,7):
                colName = columnNames[col_num]
                plt.plot(times[ICUmask],bc_origin[colName][ICUmask] , label=colName ,lw=2, marker='o', color= color[col_num])
                maxVals[col_num-3] = max(maxVals[col_num-3], np.max(bc_origin[colName][ICUmask]))
                maxVals[col_num-3] = max(maxVals[col_num-3], np.max(bc_corrected[colName][ICUmaskCorr]))
            plt.ylim([-0.5, np.max(maxVals)+0.5])

            ## after correction
            plt.subplot(2, 2, 4)
            plt.title(icu+ " apres correction")
            for col_num in range(3,7):
                colName = columnNames[col_num]
                plt.plot(timesCorr[ICUmaskCorr],bc_corrected[colName][ICUmaskCorr] , label=colName ,lw=2, marker='o', color= color[col_num])
            plt.legend()
            plt.ylim([-0.5, np.max(maxVals)+0.5])


            plt.savefig(pathname+"/"+icu+"-avant-apres.png")
            plt.close(icu_num*2)
        else:
            print(icu, " n'a pas ete modifie, donc pas de plot comparatif")

        # if icu_num >4:
        #     break




def make_cumulative_the_records_that_should_be(bc_fusionnee, TOLERANCE_NB_ERREURS = 0):
    np_bc = pd_2_np(bc_fusionnee)
    ICUs = np_bc[0]
    datetimes = np_bc[1]
    np_values_7_cols = np_bc[2]
    Ndata = datetimes.shape[0]
    # n_covid_occ, n_covid_free, n_ncovid_free, n_covid_deaths, n_covid_healed, n_covid_refused, n_covid_transfered = np_values_7_cols
    N_ICUS = ICUs.unique().size

    # n_respi_total = n_covid_occ + n_covid_free
    # n_avail_beds_total = n_covid_free + n_ncovid_free

    max_day_increase = [20, 20, 20, 5, 5, 200, 20]
     # "n_covid_occ": 20, "n_covid_free": 20, "n_ncovid_free": 20, "n_covid_deaths": 5, "n_covid_healed": 5, "n_covid_refused": 200, "n_covid_transfered": 20,
    columnNames = ["n_covid_occ", "n_covid_free", "n_ncovid_free", "n_covid_deaths", "n_covid_healed", "n_covid_refused", "n_covid_transfered"]
    columnNamesFR = ["lits covid+ occupes", "lits covid+ libres", "lits non covid libres", "deces covid", "sorties covid", "refusés", "transférés"]

    suscpect_values = np.zeros((N_ICUS, 7) , dtype=bool) # (7, N_ICUS)  -> prefer:  (N_ICUS, 7) ?
    clean_data_points = list()
    for icu_num, icu in enumerate(ICUs.unique()):
        ICUrange = np.arange(Ndata)[np.array(icu == ICUs)] ## array des indices (absolus, pour pouvoir corriger) de cet ICU
        sorting = np.argsort(datetimes[ICUrange])   ## indice interne de l'ordre chronologique
        ICUrange = ICUrange[sorting] ## range des indices de cet ICU ds le bon ordre
        dates_sorted = datetimes[ICUrange][sorting]

        ## on pourrait tester que les variations du total de lit ne sont pas trop brusques.,..
        ## mais c'est deja ce que fait get_clean_daily_values
        # if  (np.abs(np.diff(n_respi_total[ICUs]))>20).sum() > 0
        total_recording_interval = np.array(dates_sorted[-1] - dates_sorted[0], dtype=float)/1e9/86400. ## in days

        ## on inspecte les colonnes qui sont censeees entre des cumulatives
        for col_num in range(3,7):
            valeurs = np_values_7_cols[col_num][ICUrange].copy()
            differentiel  = np.diff(valeurs)
            # if (differentiel <= 0).mean() > 0.20 : ## si il n'y a pas de croissance pour au moions 20% des updates, c'est louche !
            if (differentiel <-2).sum()> TOLERANCE_NB_ERREURS: # si il y a plus de une update decroissante: pas bon !

                # si la derniere valeur est elevee, c'est p-e bien une cumulative qd meme ?
                # if valeurs[-1] >= max_day_increase[col_num]*total_recording_interval :
                if valeurs[-1] >= max_day_increase[col_num]*2 :
                    pass
                    # print("il semble cependant que la derniere valeur soit elevee (>=10), et donc c'est p-e bien une cumulative qd meme ? \n", cumulative_qties[col_num][ICUrange][sorting])
                    print("icu:", icu, " - colonne ",columnNames[col_num]," suspecte (mais valeur finale ok?) : ", valeurs)
                else:
                    print("icu:", icu, " - colonne ",columnNames[col_num]," suspecte (et valeur finale faible): ", valeurs)
                    suscpect_values[icu_num, col_num] = 1
                    # raise SystemExit

        ## copie complete
        local_np_values_7_cols = np_values_7_cols[:,ICUrange]

        ## on corrige seulement les colonnes qui ont ete identifiees comme problematiques
        for col_num in range(3,7):
            if suscpect_values[icu_num, col_num] == 1 :

                ## on lisse les valeurs anormales (probablement des recup de total, donc a ne pas rajouter par dessus)
                valeurs = np_values_7_cols[col_num, ICUrange]
                for i in range(len(valeurs)):
                    if valeurs[i] > max_day_increase[col_num]:
                        valeurs[i] = 0

                ## TODO: verifier que il n y a pas eu trop de saisies du meme jour, qui vont ici
                ## faire exploser la valeur cumulee, alors que c'est juste le meme record qui a ete saisi plusieurs fois
                ## eventuellement, en fusionnant les data proches en temps , ou avec une heuristique plus subtile
                local_np_values_7_cols[col_num] = np.cumsum(valeurs)

        for i, date in enumerate(dates_sorted):
            new_data_point = {'datetime': dates_sorted[i], 'date': dates_sorted[i],\
                                'icu_name': icu, \
                                'n_covid_occ' :             local_np_values_7_cols[0][i], \
                                'n_covid_free' :            local_np_values_7_cols[1][i], \
                                'n_ncovid_free' :           local_np_values_7_cols[2][i], \
                                'n_covid_deaths' :          local_np_values_7_cols[3][i], \
                                'n_covid_healed' :          local_np_values_7_cols[4][i], \
                                'n_covid_refused' :         local_np_values_7_cols[5][i], \
                                'n_covid_transfered' :      local_np_values_7_cols[6][i] }
            clean_data_points.append(new_data_point)

    print("bilan global: il y a eu ", suscpect_values.sum() , " colonnes a corriger, et pour les 7 colonnes, ce nbre d'ICUS 'faux': ", suscpect_values.sum(axis=0), "")
    bc_corrected = pd.DataFrame(clean_data_points)
    return bc_corrected


bc_raw = predicu.data.load_icubam_data(icubam_bedcount_path)
bc_raw["datetime"]=pd.to_datetime(bc_raw["date"])
## pandas 2 numpy


debug_mode = 0
full_plots = 1

bc_fusionnee = predicu.data.aggregate_multiple_inputs(bc_raw)
if full_plots :
    plot_compare_2_dataBases(bc_raw, bc_fusionnee, False , "fusionnee") ## 37 "erreurs" sur 39 ICUs


# bc_origin = np_2_pd( pd_2_np(bc_raw) ) # en effet, ma conversion change l'ordre des data (sans changer les data elles meme)
if debug_mode :
    # plot_compare_2_dataBases(bc_raw, bc_origin, False, "test--origin")## -> ne plot rien ! :D parfait.
    deltatmax_secondes = 900 # 15 minutes
    print("ce code la est casse, mais peu importe, la version de valentin fonctionne")
    bc_fusionnee1 = fusion_saisies_tres_rapprochees(bc_raw, deltatmax_secondes) ## BROKEN !!
    plot_compare_2_dataBases(bc_raw    , bc_fusionnee1, False , "test--fusionnee1=broken")


bc_corrected0Original = make_cumulative_the_records_that_should_be(bc_fusionnee, 0)
bc_corrected1Original = make_cumulative_the_records_that_should_be(bc_fusionnee, 1)
bc_corrected2Original = make_cumulative_the_records_that_should_be(bc_fusionnee, 2)
plot_compare_2_dataBases(bc_fusionnee, bc_corrected0Original, False, "fusion-vs-corrigeeVersion1-tolerance=0") ## 20 sorties
plot_compare_2_dataBases(bc_fusionnee, bc_corrected1Original, False, "fusion-vs-corrigeeVersion1-tolerance=1") ## ->  5 sorties
plot_compare_2_dataBases(bc_fusionnee, bc_corrected2Original, False, "fusion-vs-corrigeeVersion1-tolerance=2") #-> seul gentilly sort

plot_compare_2_dataBases(bc_raw, bc_corrected0Original, False, "brute-vs-corrigee-tolerance=0") #-> seul gentilly sort
# plot_compare_2_dataBases(bc_raw, bc_corrected1Original, False, "brute-vs-corrigee-tolerance=1") #-> seul gentilly sort
# plot_compare_2_dataBases(bc_raw, bc_corrected2Original, False, "brute-vs-corrigee-tolerance=2") #-> seul gentilly sort

if debug_mode:
    bc_corrected0 = predicu.data.fix_noncum_inputs(bc_fusionnee, 0)
    bc_corrected1 = predicu.data.fix_noncum_inputs(bc_fusionnee, 1)
    bc_corrected2 = predicu.data.fix_noncum_inputs(bc_fusionnee, 2)
    # if full_plots :
    plot_compare_2_dataBases(bc_fusionnee, bc_corrected0, False, "fusion-vs-corrigee-tolerance=0") ## 20 sorties
    plot_compare_2_dataBases(bc_fusionnee, bc_corrected1, False, "fusion-vs-corrigee-tolerance=1") ## ->  5 sorties
    plot_compare_2_dataBases(bc_fusionnee, bc_corrected2, False, "fusion-vs-corrigee-tolerance=2") #-> seul gentilly sort

    plot_compare_2_dataBases(bc_corrected0Original, bc_corrected0, True , "test--corrigee_tol=0-vs-Valentin_tol=0") ## -> ne plot rien ! :D parfait.
    plot_compare_2_dataBases(bc_corrected1Original, bc_corrected1, True , "test--corrigee_tol=1-vs-Valentin_tol=1") ## -> ne plot rien ! :D parfait.
    plot_compare_2_dataBases(bc_corrected2Original, bc_corrected2, True , "test--corrigee_tol=2-vs-Valentin_tol=2") ## -> ne plot rien ! :D parfait.

if debug_mode:
    ## self-consitency check ##
    print("\nNow performing a simle self-consitency check.")
    bc_corrected_twice = make_cumulative_the_records_that_should_be(bc_corrected0, 0)
    plot_compare_2_dataBases(bc_corrected0, bc_corrected_twice, False , "test--corr-vs-vorrTwice") ## -> ne plot rien ! :D parfait.


if debug_mode:
    ## ce qui suit, ca chie ##
    print("start get_clean_daily_values(bc_corrected)")
    bc_cleaned0 = predicu.data.get_clean_daily_values(bc_corrected0Original)
    plot_compare_2_dataBases(bc_corrected0Original, bc_cleaned0,  False, "corrige_tol=0-vs-+cleaned")
    bc_cleaned1 = predicu.data.get_clean_daily_values(bc_corrected1Original)
    plot_compare_2_dataBases(bc_corrected1Original, bc_cleaned1,  False, "corrige_tol=1-vs-+cleaned")




# raise SystemExit



# def plot_each_icu_separately(bc, suffix):
#     pathname = 'figs-ICUs-1-par-1'
#     if not os.path.exists(pathname):
#         os.makedirs(pathname)

#     np_bc = pd_2_np(bc)
#     ICUs = np_bc[0]
#     datetimes = np_bc[1]
#     np_values_7_cols = np_bc[2]
#     Ndata = datetimes.shape[0]
#     n_covid_occ, n_covid_free, n_ncovid_free, n_covid_deaths, n_covid_healed, n_covid_refused, n_covid_transfered = np_values_7_cols

#     n_respi_total = n_covid_occ + n_covid_free
#     n_avail_beds_total = n_covid_free + n_ncovid_free


#     # T0 = np.min(datetimes) # premier record (jour)
#     T0 = np.datetime64('2020-03-17T00:00:00.000000000')
#     times = np.array((bc['datetime']-T0), dtype=float)/86400.0/1.e9
#     # times = bc['datetime']

#     columnNames = ["n_covid_occ", "n_covid_free", "n_ncovid_free", "n_covid_deaths", "n_covid_healed", "n_covid_refused", "n_covid_transfered"]
#     columnNamesFR = ["lits covid+ occupes", "lits covid+ libres", "lits non covid libres", "deces covid", "sorties covid", "refusés", "transférés"]

#     for icu_num, icu in enumerate(bc["icu_name"].unique()):
#         ICUmask = (icu == bc["icu_name"])

#         plt.figure(icu_num,[10,10])
#         plt.title(icu+" données instantanées")

#         n_entrants = bc["n_covid_occ"][ICUmask] +bc["n_covid_occ"][ICUmask]

#         plt.subplot(1, 2, 1)
#         plt.plot(times[ICUmask],n_respi_total[ICUmask] , label='total lits covid' , lw=2, marker='o')
#         plt.plot(times[ICUmask],n_entrants[ICUmask] , label='total entrants' , lw=2, marker='o')
#         plt.plot(times[ICUmask],n_demandants[ICUmask] , label='total demandes' , lw=2, marker='o')
#         for col_num in range(1,3):
#             colName = columnNames[col_num]
#             plt.plot(times[ICUmask],bc[colName][ICUmask] , label=colName , lw=2, marker='o')
#         plt.legend()
#         plt.ylim([-0.5,40])
#         plt.xlabel("jours (depuis 17 mars)") # depuis 17 mars
#     #     plt.savefig("figs/n_occ_"+icu+".png")
#         #plt.figure(icu_num*2+1,[10,10])

#         # plt.subplot(1, 2, 2)
#         # plt.title(icu+" données cumulatives")
#         # for col_num in range(3, 7):
#         #     colName = columnNames[col_num]
#         #     plt.plot(times[ICUmask],bc[colName][ICUmask] , label=colName , lw=2, marker='o')
#         # plt.legend()
#         # # plt.ylim([-1,15])
#         # plt.xlabel("jours") # depuis 17 mars

#         # plt.savefig(pathname+"/"+icu+"_fixedWindow_"+suffix+".png")
#         # plt.close(icu_num)

#         if icu_num >3:
#             break

# # plot_each_icu_separately(bc_corrected0, "donnees_corrigees_tol=0")
# # plt.show()

# plot_each_icu_separately(bc, "donnees_brutes")



# ## 'fusionne' les donnees lorsque 2 saisies sont tres proches dans le temps
# def fusion_saisies_tres_rapprochees(bc, deltatmax_secondes):
#     deltatmax_secondes_np_timedeltat64 = np.timedelta64(deltatmax_secondes,'s') # datetime.timedelta(days=0,seconds=3600)
#     nBcorrection = 0

#     np_bc = pd_2_np(bc)
#     ICUs = np_bc[0]
#     datetimes = np_bc[1]
#     np_values_7_cols = np_bc[2]
#     Ndata = datetimes.shape[0]

#     indices_a_eliminer = []
#     for icu_num, icu in enumerate(bc["icu_name"].unique()):
#         ICUrange = np.arange(Ndata)[np.array(icu == bc["icu_name"])] ## array des indices (absolus, pour pouvoir corriger) de cet ICU
#         sorting = np.argsort(datetimes[ICUrange])   ## indice interne de l'ordre chronologique
#         ICUrange = ICUrange[sorting] ## range des indices de cet ICU ds le bon ordre
#         for i, index_absolu in enumerate(ICUrange):
#             if i>0: # so that we can compare woth the previous one
#                 assert(ICUrange[i] == index_absolu) ## this is a comment
#                 deltat = np.timedelta64(datetimes[ICUrange[i]] - datetimes[ICUrange[i-1]] ,'m')
#                 ## si 2 saisies en moins de  XX secondes, alors :
#                 if deltat < deltatmax_secondes_np_timedeltat64 :

#                     ##TODO: se souvenir des indices a enlever (ou a garder) + les uppriemr a la fin
#                     if np.array_equal(np_values_7_cols[:,ICUrange[i]], np_values_7_cols[:,ICUrange[i-1]]) == False: ## pas de flag si 2 saisies identiques
#                         indices_a_eliminer.append(ICUrange[i-1])
#                         print(icu, deltat)
#                         print(np_values_7_cols[:,ICUrange[i]])
#                         print(np_values_7_cols[:,ICUrange[i-1]])
#                         ## choix par defaut: remplacer les 2 valeurs par le max (colonne par colonne)
#                         np_values_7_cols[:,ICUrange[i]]   = np.maximum(np_values_7_cols[:,ICUrange[i]], np_values_7_cols[:,ICUrange[i-1]])
#                         np_values_7_cols[:,ICUrange[i-1]] = np_values_7_cols[:,ICUrange[i]]
#                         nBcorrection += 1

#     print("il y a eu ", nBcorrection,   " corrections, à comparer avec ", bc.shape, "  ou plutot ", bc.shape[0])
#     indices_a_eliminer= np.sort(np.array(indices_a_eliminer).copy())
#     print(indices_a_eliminer)


# ## TODO !! Ici j'ai un souci d'indices, clairement ##

#     # ICUs              = ICUs.drop(index= indices_a_eliminer) #               = np.delete(ICUs,             indices_a_eliminer, axis=0)
#     # ICUs = list(ICUs)
#     # for index in sorted(indices_a_eliminer, reverse=True):
#     #     del ICUs[index]
#     # ICUs = pd.DataFrame(ICUs)
#     ICUs = ICUs.drop(labels= indices_a_eliminer, axis=0)

#     datetimes         = np.delete(datetimes,          indices_a_eliminer, axis=0)
#     np_values_7_cols  = np.delete(np_values_7_cols[:,], indices_a_eliminer, axis=1)

#     # ICUrange = np.delete(ICUrange, indices_a_eliminer)
#     # ICUs              = ICUs[ICUrange] # .drop(index= indices_a_eliminer) #               = np.delete(ICUs,             indices_a_eliminer, axis=0)
#     # datetimes         = datetimes[ICUrange]
#     # np_values_7_cols  = np_values_7_cols[:,ICUrange]

#     np_bc = [ICUs, datetimes, np_values_7_cols]
#     bc_fusionnee = np_2_pd(np_bc)
#     return bc_fusionnee
