''' This script contains scientific functions that I use in analying the MITgcm output'''

def seaice_thickness(Q_ice, delta_t):
    """Change in sea ice thickness (m) due to constant heat supply Q_ice (W/m^2s) over time delta_t (s)"""
    L = 2.5e5
    rho_ice = 900
    h_ice = -Q_ice*delta_t / (rho_ice*L)
    return h_ice

def F_s_seaice(Q_ice):
    """Salt flux due to change in sea ice mass due to constatn heat supply  Q_ice (W/m^2s) over time delta_t (s)"""
    sigma = 30 # change in mass salinity between sea ice and seawater
    L = 2.5e5
    F_s = Q_ice * sigma / L
    return F_s