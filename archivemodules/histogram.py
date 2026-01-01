# fichier qui trace l'histogramme de la densité du vecteur TIE

import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
from scipy import stats

def histogram(TIE, scale=5, plot_kde = False) :

    mean = stat.mean(TIE)
    std = stat.stdev(TIE)

    # Méthode de Freedman-Diaconis pour calculer les bins
    q75, q25 = np.percentile(TIE, [75 ,25])
    iqr = q75 - q25
    bin_width = 2 * iqr / (len(TIE) ** (1/3))
    bins = int((np.max(TIE) - np.min(TIE)) / bin_width)

    # debug
    print("bins :", bins)
    print("max :",np.max(TIE), "\nmin :", np.min(TIE))
    print("mean :", mean)
    print("std :", std)

    plt.figure(figsize=(8, 4))
    plt.hist(TIE, bins=bins, density=True, alpha=0.6, color='b')
    plt.xlabel('Value [s]')
    plt.ylabel('Probability density')
    plt.title('TIE Histogram')
    plt.axvline(x=100*1e-9, color='r', linestyle='--', label = f'value limit : 100 ns')
    plt.axvline(x=-100*1e-9, color='r', linestyle='--')
    plt.axvline(x=mean+3*std, color='g', linestyle=':', label = f'3 x std : 3 x {(std*1e9):.3f} ns')
    plt.axvline(x=mean-3*std, color='g', linestyle=':')
    plt.axvline(x=mean, color='g', linestyle='-.', label = f'mean : {(mean*1e9):.3f} ns')
    plt.legend()
    plt.figtext(0.8, 0.95, f"max = {(np.max(TIE)*1e9):.3f} ns")
    plt.figtext(0.8, 0.9, f"min = {(np.min(TIE)*1e9):.3f} ns")
    plt.grid()

    if plot_kde :
        kde1 = stats.gaussian_kde(TIE)
        kde2 = stats.gaussian_kde(TIE, bw_method='silverman')
        fig = plt.figure(figsize=(8, 4))
        plt.xlabel('Value [s]')
        plt.ylabel('Probability density')
        plt.title('TIE Gaussian estimation')
        nbr_point_resolution = 100
        x_eval = np.linspace(mean-scale*std, mean+scale*std, num=nbr_point_resolution) 
        plt.plot(x_eval, kde1(x_eval), 'k-', label="Scott's Rule")
        plt.plot(x_eval, kde2(x_eval), 'r-', label="Silverman's Rule")
        plt.legend()

    return mean, std