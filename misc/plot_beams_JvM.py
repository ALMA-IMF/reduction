# Script that extract and plots array of beams from CASA cube

import os
import glob
from astropy.io import fits
import matplotlib.pyplot as plt

### Modified by user ###

# Necessary for basenames
fields = ['G333.60']
bands = ['B6']
spws = ['spw0']
arrays = ['12M']

# Paths and extensions
cube_path = '/lustre/roberto/ALMA_IMF/lines/hypergator/fullcubes_12m'
cube_ext = '.image.pbcor.mincube.fits' #preserve the initial dot
jvm_ext = '.JvM.image.fits' #preserve the initial dot
cont_path = '/lustre/roberto/ALMA_IMF/February2021Release'

# In case it is wanted to cut a few edge channels in plot of cube.
low_chans = 0 # Channels to cut
high_chans = 0 #Channels to cut

#########################


for field in fields:
    for band in bands:
        for spw in spws:
            for array in arrays:
                # Cube name
                cube_name = '{0}_{1}_{2}_{3}_{2}{4}'.format(field,band,spw,array,cube_ext)
                cube_file = os.path.join(cube_path,cube_name)
                print('Cubename is: {}'.format(cube_name))
                # JvM cube name
                jvm_name = '{0}_{1}_{2}_{3}_{2}{4}'.format(field,band,spw,array,jvm_ext)
                jvm_file =  os.path.join(cube_path,jvm_name)
                print('JvM cubename is: {}'.format(jvm_name))
                # Continuum image name. Last finaliter imagename is taken if more than one.
                cont_path = os.path.join(cont_path,field,band,'cleanest')
                print('Continuum path is: {}'.format(cont_path))
                cont_files = glob.glob(cont_path+'/*finaliter*pbcor.fits')
                cont_file = cont_files[-1]
                print('Continuum filename is: {}'.format(cont_file))

                # Cube beams
                hdu_cube = fits.open(cube_file)
                cube_hd = hdu_cube[0].header
                beam_hd = hdu_cube[1].header
                beam_data = hdu_cube[1].data
                hdu_cube.close()

                bmaj_list = []
                bmin_list = []
                for beam in range(beam_data.shape[0]):
                    bmaj_list.append(beam_data[beam][0])
                    bmin_list.append(beam_data[beam][1])

                # JvM cube beams
                jvm_cube = fits.open(jvm_file)
                jvm_hd = jvm_cube[0].header
                jvm_bmaj = jvm_hd['BMAJ']*3600.
                jvm_bmin = jvm_hd['BMIN']*3600.
                jvm_cube.close()

                # Continuum beams
                cont_im = fits.open(cont_file)
                cont_hd = cont_im[0].header
                cont_bmaj = cont_hd['BMAJ']*3600.
                cont_bmin = cont_hd['BMIN']*3600.
                cont_im.close()

                #Plotting
                fig, ax = plt.subplots(figsize=(9,6))

                ax.plot(bmaj_list[low_chans : len(bmaj_list) - 1 - high_chans], label='BMAJ_cube', linewidth=2, color='r')
                ax.plot(bmin_list[low_chans : len(bmin_list) - 1 - high_chans], label='BMIN_cube', linewidth=2, color='b')
                ax.axhline(y=cont_bmaj, linewidth=2, color='k', linestyle='dashed', label='BMAJ_cont')
                ax.axhline(y=cont_bmin, linewidth=2, color='k', linestyle='dashdot', label='BMIN_cont')
                ax.axhline(y=jvm_bmaj, linewidth=2, color='g', linestyle='dashed', label='BMAJ_JvM')
                ax.axhline(y=jvm_bmin, linewidth=2, color='g', linestyle='dashdot', label='BMIN_JvM')
                ax.set_title(jvm_name, fontsize=14)
                ax.set_ylabel('arcsec', fontsize=14)
                ax.set_xlabel('channel', fontsize=14)
                ax.legend(loc='best', fontsize=12)

                #fig.show()
                #fig.clf()
                plot_file = os.path.join(cube_path,jvm_name+'.beam_comparison.png')
                fig.savefig(plot_file)

