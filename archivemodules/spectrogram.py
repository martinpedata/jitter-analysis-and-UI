# fichier qui calcul le spectre du vecteur TIE avec une FFT et la PSD du signal sync0 reconstitué

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
import scipy.signal as sc

def spectroplot_TIE(TIE):
    Y = fft(TIE)
    freqs = np.arange(0,len(TIE), 1)

    # Calcul du spectre de puissance (en dB)
    power_spectrum = np.abs(Y)**2

    plt.figure(figsize=(10, 5))
    plt.plot(freqs[:len(TIE)//2], 10 * np.log10(power_spectrum[:len(TIE)//2]))
    plt.title("Spectre de puissance du TIE")
    plt.xlabel("Fréquence [Hz]")
    plt.ylabel("Puissance [dB]")
    plt.grid(True)

def spectroplot_signal(period, time, data_ref, data, plot_F = False):
    if plot_F :
        fig, axs = plt.subplots(2, 2, figsize=(10,8))
        axs[0,0].plot(time, data_ref)
        axs[0,0].set_xlabel("time [s]")
        axs[0,0].set_ylabel("Amplitude [V]")
        axs[0,0].set_title("Signal sync0 of slave 1")
        axs[0,1].plot(time, data)
        axs[0,1].set_xlabel("time [s]")
        axs[0,1].set_ylabel("Amplitude [V]")
        axs[0,1].set_title("Signal sync0 of slave #")
        w, h = sc.freqz(data_ref, 1, worN = 2048, fs=1/period, whole=False)
        axs[1,0].plot(w, 20*np.log10(abs(h)))
        axs[1,0].set_xlabel("Frequency (Hz)")
        axs[1,0].set_ylabel("Magnitude (dB)")
        axs[1,0].set_title("Fourier Transform of signal")
        axs[1,0].grid()
        w, h = sc.freqz(data, 1, worN = 2048, fs=1/period, whole=False)
        axs[1,1].plot(w, 20*np.log10(abs(h)))
        axs[1,1].set_xlabel("Frequency (Hz)")
        axs[1,1].set_ylabel("Magnitude (dB)")
        axs[1,1].set_title("Fourier Transform of signal")
        axs[1,1].grid()

    # Paramètres PSD
    nperseg = 4096

    # Calcul de la PSD pour le peigne régulier
    f_slave1, psd_slave1 = sc.welch(data_ref, fs=1/period, nperseg=nperseg)
   
    # Calcul de la PSD pour le peigne jitteré
    f_slavex, psd_slavex = sc.welch(data, fs=1/period, nperseg=nperseg)
   
    # Affichage
    plt.figure(figsize=(10, 5))
    plt.plot(f_slave1, 10*np.log10(psd_slave1), label="Slave ref", color='blue')
    plt.plot(f_slavex, 10*np.log10(psd_slavex), label="Slave #", color='orange')
    plt.title("Densité Spectrale de Puissance (PSD)")
    plt.xlabel("Fréquence [Hz]")
    plt.ylabel("PSD [dB]")
    plt.grid()
    plt.legend()