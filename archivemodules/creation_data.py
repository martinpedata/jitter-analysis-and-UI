# file with all the needed functions to create an artificial TIE and an artificial signal sync0 based on this TIE vector

# required libraries
import numpy as np
import matplotlib.pyplot as plt

def generate_random_jitter(sigma, mu, size):
    jitter = np.random.normal(mu, sigma, size)
    return jitter

def generate_deterministic_jitter(jitter_frequency, jitter_amplitude, jitter_offset, size):
    # creation of a vector 'jitter' containing sinusoidal values at jitter_frequency center on 0 and with an amplitude of 'jitter_amplitude' and an time offset of 'jitter_offset'

    k = np.arange(jitter_offset, size+jitter_offset) # vector of time samples
    jitter = 0 # posibility to adjust the amplitude offset
    for i, amplitude in enumerate(jitter_amplitude) :
        jitter += amplitude * np.sin(2 * np.pi * k * jitter_frequency[i])
    return jitter

def creation_data(size, parameters):
    period = parameters["period"]
    period_sync0 = parameters["period_sync0"]
    time_offset = parameters["time_offset"]
    sigma = parameters["sigma"]
    mu = parameters["mu"]
    frequency = parameters["frequency"]
    offset = parameters["offset"]
    amplitude = parameters["amplitude"]

    print("mean imposed :", mu)
    print("std imposed :", sigma)
    print("frequency imposed :", frequency)
    TIE = (generate_random_jitter(sigma, mu, size) + generate_deterministic_jitter(frequency, amplitude, offset, size))/2
    return period, period_sync0, time_offset, TIE #period |b| to sync0, duration of sync0=1, time of the first sync0, Time Interval Error |b| slave_1 and slave_x

def creation_vecteur_data(period, period_sync0, time_offset, TIE):
    sample_frequency = 20/period_sync0 #[Sample/s] to have 20 samples for the sync0
    size = len(TIE)
    duration = size*period #[s]

    # Vectors of slave_1
    time_ref = np.arange(0, duration, 1/sample_frequency)
    data_ref = np.zeros_like(time_ref)

    nbr_sync0=0
    for i, t in enumerate(time_ref):
        if t >= time_offset + nbr_sync0*period and t < time_offset + period_sync0 + nbr_sync0*period :
            data_ref[i] = 1
        if t >= time_offset + period_sync0 + nbr_sync0*period :
            nbr_sync0 += 1
    if size == nbr_sync0 :
        print('Creation successful')
    else :
        print('!!!Creation unsuccessful!!!')

    # Vectors of slave_x
    data = np.zeros_like(time_ref)

    nbr_sync0=0
    for i, t in enumerate(time_ref):
        if nbr_sync0 == size :
            break
        if t-TIE[nbr_sync0] >= time_offset + nbr_sync0*period and t < time_offset + period_sync0 + nbr_sync0*period :
            data[i] = 1
        if t-TIE[nbr_sync0] >= time_offset + period_sync0 + nbr_sync0*period :
            nbr_sync0 += 1

    return time_ref, data_ref, data