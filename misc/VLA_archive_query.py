# Modified 14.11.2018 by Roberto Galvan-Madrid
# Modified 19.07.2019 by Adam Ginsburg
# Modified 20.07.2019 by Roberto Galvan-Madrid
# Script that queries and downloads JVLA data for ALMA-IMF
# Desired JVLA data: 0.37 arcsec, C, X, Ku, K bands (probably add Q), "continuum" mode
# Freq/Band     A       B       C       D       Selected configs        FOV FWHM arcmin
# 6.0 GHz (C)   0.33    1.0     3.5     12      A, AB, BnA              7.5             
# 10 GHz (X)    0.20    0.60    2.1     7.2     A, AB, BnA, B           4.5                             
# 15 GHz (Ku)   0.13    0.42    1.4     4.6     A, AB, BnA, B           3.0
# 22 GHz (K)    0.089   0.28    0.95    3.1     B, BC, CnB, C           2.05
# 45 GHz (Q)    0.043   0.14    0.47    1.5     B, BC, CnB, C           1.0       

from astroquery.nrao import Nrao
import astropy.units as u
import astropy.coordinates as coord
from astropy.table import Table
import numpy as np


targets = [['W51-E','19h23m44.1800s','+14d30m29.500s'],
           ['W43-MM2','18h47m36.6100s','-02d00m51.100s'],
           ['W43-MM3','18h47m41.4600s','-02d00m27.600s'],
           ['G337.92','16h41m10.6200s','-47d08m02.900s'],
           ['G338.93','16h40m34.4200s','-45d41m40.600s'],
           ['G328.25','15h57m59.6800s','-53d58m00.200s'],
           ['G327.29','15h53m08.6200s','-54d35m30.800s'],
           ['W51-IRS2','19h23m39.8100s','+14d31m03.500s'],
           ['G333.60','16h22m09.3600s','-50d05m58.900s'],
           ['W43-MM1','18h47m47.0000s','-01d54m26.000s'],
           ['G008.67','18h06m19.2600s','-21d37m26.700s'],
           ['G353.41','17h30m26.2800s','-34d41m49.700s'],
           ['G010.62','18h10m28.8400s','-19d55m48.300s'],
           ['G012.80','18h14m13.3700s','-17d55m45.200s'],
           ['G351.77','17h26m42.6200s','-36d09m20.500s']]

#targets = [['W51-E','19h23m44.1800s','+14d30m29.500s'], ['G010.62','18h10m28.8400s','-19d55m48.300s']]
#targets = [['G010.62','18h10m28.8400s','-19d55m48.300s']]
#targets = [['W51-IRS2','19h23m39.8100s','+14d31m03.500s'],\
#['G010.62','18h10m28.8400s','-19d55m48.300s']]

data_tables = {}
for element,(targetname, ra, dec) in enumerate(targets):
    print(targets[element])
    target_table = []
    #
    print('C-band')
    C_result_table = Nrao.query_region(coord.SkyCoord(targets[element][1],targets[element][2],
                                                      frame='icrs'),
                                       radius=3.75*u.arcmin,
                                       telescope='jansky_vla', obs_band='C',
                                       telescope_config=['A','AB','BnA'])
    C_result_table.remove_rows(np.where(C_result_table['Bandwidth'] != 128.0))
    #print(C_result_table)
    C_result_table.write(targets[element][0]+'_C-band.dat', format='ascii', overwrite=True)
    target_table.append(C_result_table)
    #
    print('X-band')
    X_result_table = Nrao.query_region(coord.SkyCoord(targets[element][1],targets[element][2],
                                                      frame='icrs'),
                                       radius=2.25*u.arcmin,
                                       telescope='jansky_vla',
                                       obs_band='X',
                                       telescope_config=['A','AB','BnA','B'])
    X_result_table.remove_rows(np.where(X_result_table['Bandwidth'] != 128.0))
    #print(X_result_table)
    X_result_table.write(targets[element][0]+'_X-band.dat', format='ascii', overwrite=True)
    target_table.append(X_result_table)
    #
    print('Ku-band')
    Ku_result_table = Nrao.query_region(coord.SkyCoord(targets[element][1],targets[element][2],
                                                       frame='icrs'),
                                        radius=1.5*u.arcmin,
                                        telescope='jansky_vla', obs_band='U',
                                        telescope_config=['A','AB','BnA','B'])
    Ku_result_table.remove_rows(np.where(Ku_result_table['Bandwidth'] != 128.0))
    #print(Ku_result_table)
    Ku_result_table.write(targets[element][0]+'_Ku-band.dat', format='ascii', overwrite=True)
    target_table.append(Ku_result_table)
    #
    print('K-band')
    K_result_table = Nrao.query_region(coord.SkyCoord(targets[element][1],targets[element][2],
                                                      frame='icrs'),
                                       radius=1.02*u.arcmin,
                                       telescope='jansky_vla', obs_band='K',
                                       telescope_config=['B','BC','CnB','C',])
    K_result_table.remove_rows(np.where(K_result_table['Bandwidth'] != 128.0))
    #print(K_result_table)
    K_result_table.write(targets[element][0]+'_K-band.dat', format='ascii', overwrite=True)
    target_table.append(K_result_table)
    #
    print('Q-band')
    Q_result_table = Nrao.query_region(coord.SkyCoord(targets[element][1],targets[element][2],
                                                      frame='icrs'),
                                       radius=0.5*u.arcmin,
                                       telescope='jansky_vla', obs_band='Q',
                                       telescope_config=['B','BC','CnB','C'])
    Q_result_table.remove_rows(np.where(Q_result_table['Bandwidth'] != 128.0))
    #print(Q_result_table)
    Q_result_table.write(targets[element][0]+'_Q-band.dat', format='ascii', overwrite=True)
    target_table.append(Q_result_table)
    #
    print('Data table for {} is:'.format(targets[element][0]))
    print(target_table)
    data_tables[targetname] = {'Q': Q_result_table,
                               'K': K_result_table,
                               'Ku': Ku_result_table,
                               'X': X_result_table,
                               'C': C_result_table,
                              }



    #result_table = Nrao.query_region(coord.SkyCoord(targets[element][1],targets[element][2], \
    #frame='icrs'), radius=5*u.arcmin, telescope='jansky_vla', freq_low=4001*u.MHz, \
    #freq_up=7999*u.MHz, telescope_config=['A','AB'])
