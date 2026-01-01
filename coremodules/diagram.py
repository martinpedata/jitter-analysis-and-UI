
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors

'''Module contenant toutes les fonctions nécessaires à calculer la distibution du vecteur TIE
et créer un graphique qui représente une mesure comme avec un oscilloscope et calculer les paramètres de probabilité'''

# flant montant à 0 (référence)
# fonction permetant de simuler un flanc montant habituel (pas parfaitement vertical) 
def smooth_rising_edge(t, center=0, width=2): 
    return 0.5 * (1 + np.tanh((t - center) / width))


# fonction pour calculer la densité sur base des paramètres de probabilité du vecteur TIE
def density(TIE, mean, std, scale=5):
    
    # Axe de temps local centré sur le front idéal (en ns)
    nbr_point_resolution = 1000 
    time = np.linspace(mean-scale*std, mean+scale*std, nbr_point_resolution) #[s] 
    # Initialiser la densité temporelle
    density = np.zeros_like(time)

    for t_ns in TIE:
        # Ajouter chaque flanc de forme sigmoide centrée sur t_ns
        signal = smooth_rising_edge(time, center=t_ns, width=1.5)
        # On dérive le signal pour obtenir une "impulsion" autour du front (= une densité)
        dsignal = np.gradient(signal, time)
        density += dsignal

    # Normalisation de la densité pour l’utiliser comme alpha dans oscilloplot
    density /= np.max(density)

    return density


def oscilloplot(TIE, mean, std, density, scale=5, plot_oscillo=False, plot_fondu=False):

    # Axe de temps local centré sur le front idéal (en ns)
    nbr_point_resolution = 1000 
    time = np.linspace(mean-scale*std, mean+scale*std, nbr_point_resolution) #[s] 

    # Création des figures
    if plot_oscillo :
        fig, ax = plt.subplots(1,1, figsize=(8, 4)) 
        for t_ns in TIE:
            # Ajouter chaque flanc de forme sigmoide centrée sur t_ns
            signal = smooth_rising_edge(time, center=t_ns, width=1.5)
            ax.plot(time, signal, color='blue', linewidth=0.5)

        # Mise en forme 
        ax.set_xlabel("Temps [ns]") 
        ax.set_ylabel("Amplitude") 
        ax.set_title("Superposition des flancs montants (avec TIE)") 
        ax.axvline(0, color='black', linestyle='--', linewidth=1) 
        ax.grid()

    fig, ax1 = plt.subplots(1,1, figsize=(8, 4))
    if plot_fondu :
        fig, ax2 = plt.subplots(1,1, figsize=(8, 4))

    # Création de la colormap
    norm = colors.Normalize(vmin=np.min(density), vmax=np.max(density))
    colormap = matplotlib.colormaps['hot_r'] # choix colormap voir https://matplotlib.org/stable/gallery/color/colormap_reference.html
    cmap = colors.ListedColormap(colormap(np.linspace(0.3, 0.95, 256)))

    # Tracer les flancs avec alpha dépendant de la densité locale
    for t_ns in TIE:
        signal = smooth_rising_edge(time, center=t_ns, width=1.5)
        
        # On récupère la densité locale au centre du flanc
        density_local = density[np.abs(time - t_ns).argmin()]

        # On récupère la couleur adéquate
        color = cmap(norm(density_local))
        ax1.plot(time, signal, color=color, linewidth=0.5)

        if plot_fondu :
            # ou Alpha en fonction de la densité (plus dense → plus opaque)
            alpha = 1e-10 + (1-(1e-10)) * density_local  # évite alpha=0
            ax2.plot(time, signal, color='blue', alpha=alpha, linewidth=0.5)

    # Ajout de la colorbar
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    fig1 = ax1.get_figure()
    fig1.colorbar(sm, ax=ax1, label='Densité')

    # Mise en forme
    ax1.set_xlabel("Temps [ns]")
    ax1.set_ylabel("Amplitude")
    ax1.set_title("Flancs montants pondérés par leur densité temporelle")
    ax1.axvline(0, color='black', linestyle='--', linewidth=1)
    ax1.axvline(x=100, color='r', linestyle='--', label = f'value limit : 100 ns')
    ax1.axvline(x=-100, color='r', linestyle='--')
    ax1.grid()

    if plot_fondu :
        ax2.set_xlabel("Temps [ns]")
        ax2.set_ylabel("Amplitude")
        ax2.set_title("Flancs montants pondérés par leur densité temporelle")
        ax2.axvline(0, color='black', linestyle='--', linewidth=1)
        
    return fig1