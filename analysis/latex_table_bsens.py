import numpy as np
from astropy.table import Table, Column
from astropy import table
import requests
import keyring
from astropy import units as u
import datetime

from latex_info import (latexdict, format_float, round_to_n, rounded,
                        rounded_arr, strip_trailing_zeros, exp_to_tex)

latexdict = latexdict.copy()

if datetime.datetime.today() > datetime.datetime(year=2021, month=1, day=10):
    result = requests.get('https://bio.rc.ufl.edu/secure/adamginsburg/ALMA-IMF/October2020Release/tables/metadata_bsens_cleanest.ecsv',
                          auth=('almaimf', keyring.get_password('almaimf', 'almaimf')))
    with open('metadata_bsens_cleanest.ecsv', 'w') as fh:
        fh.write(result.text)


    result = requests.get('https://bio.rc.ufl.edu/secure/adamginsburg/ALMA-IMF/tables/bandpass_fraction.ecsv',
                          auth=('almaimf', keyring.get_password('almaimf', 'almaimf')))
    with open('bandpass_fraction.ecsv', 'w') as fh:
        fh.write(result.text)

bp_tbl = Table.read('bandpass_fraction.ecsv')
bp_tbl['band'] = [f'B{b}' for b in bp_tbl['band']]
bp_tbl.rename_column('field','region')
bp_tbl = table.join(bp_tbl.group_by('config').groups[0], bp_tbl.group_by('config').groups[1], keys=('region', 'band'))
bp_tbl.rename_column('bwfrac_1', '12Mlong_frac')
bp_tbl.rename_column('bwfrac_2', '12Mshort_frac')
bp_tbl.remove_column('config_1')
bp_tbl.remove_column('config_2')

tbl = table.join(Table.read('metadata_bsens_cleanest.ecsv'), bp_tbl, keys=('region', 'band'))
bad = np.array(['diff' in x for x in tbl['filename']])

# downselect (need bsens=true to avoid duplication - but be wary in case you remove duplicates upstream!)
keep = ((tbl['suffix'] == 'finaliter') &
        (tbl['robust'] == 'r0.0') &
        (~tbl['pbcor']) &
        (tbl['bsens']) &
        (~bad))


wtbl = tbl[keep]


print(len(wtbl))
print(wtbl)

wtbl['selfcaliter'] = Column(data=[int(x[2:]) for x in wtbl['selfcaliter']])
wtbl['bsens_div_cleanest_mad'] = wtbl['mad_bsens'] / wtbl['mad_cleanest']
wtbl['bsens_div_cleanest_max'] = wtbl['max_bsens'] / wtbl['max_cleanest']
wtbl['bsens_mad_div_req'] = wtbl['mad_bsens'] / wtbl['Req_Sens'] * 1e3


cols_to_keep = {'region':'Region',
                'band':'Band',
                #'selfcaliter':'$n_{sc}$',
                #'bmaj':r'$\theta_{maj}$',
                #'bmin':r'$\theta_{min}$',
                #'bpa':'BPA',
                #'Req_Res': r"$\theta_{req}$",
                #'BeamVsReq': r"$\theta_{req}/\theta_{maj}$",
                #'peak/mad': "DR",
                #'peak':'$S_{peak}$',
                'mad_bsens':'$\sigma_{MAD}$(bsens)',
                'mad_cleanest':'$\sigma_{MAD}$(cleanest)',
                'bsens_div_cleanest_mad':'$\\frac{\sigma_{MAD}(\mathrm{bsens})}{\sigma_{MAD}(\mathrm{cleanest})}$',
                '12Mshort_frac': '$f_{BW,cleanest}$',
                'max_bsens':'$S_{peak}$(bsens)',
                'max_cleanest':'$S_{peak}$(cleanest)',
                'bsens_div_cleanest_max':'$\\frac{S_{peak}(\mathrm{bsens})}{S_{peak}(\mathrm{cleanest})}$',
                'Req_Sens': 'Requested $\sigma$',
                'bsens_mad_div_req': '$\sigma_{\mathrm{bsens}}/\sigma_{\mathrm{req}}$',
                #'dr_cleanest': "DR$_{cleanest}$",
                #'dr_bsens': "DR$_{bsens}$",
               }


units = {'$S_{peak}(bsens)$':u.Jy.to_string(u.format.LatexInline),
         '$S_{peak}(cleanest)$':u.Jy.to_string(u.format.LatexInline),
         '$\sigma_{MAD}(bsens)$':u.mJy.to_string(u.format.LatexInline),
         '$\sigma_{MAD}(cleanest)$':u.mJy.to_string(u.format.LatexInline),
         'Requested $\sigma$':u.mJy.to_string(u.format.LatexInline),
         #'$\sigma_{req}$':u.mJy.to_string(u.format.LatexInline),
         #r'$\theta_{req}$':u.arcsec.to_string(u.format.LatexInline),
         #r'$\theta_{maj}$':u.arcsec.to_string(u.format.LatexInline),
         #r'$\theta_{min}$':u.arcsec.to_string(u.format.LatexInline),
         #r'PA':u.deg.to_string(u.format.LatexInline),
        }
latexdict['units'] = units

wtbl = wtbl[list(cols_to_keep.keys())]


for old, new in cols_to_keep.items():
    if old in wtbl.colnames:
        #wtbl[old].meta['description'] = description[old]
        wtbl.rename_column(old, new)
        if new in units:
            wtbl[new].unit = units[new]

for colname in ['$\sigma_{MAD}$(bsens)', '$\sigma_{MAD}$(cleanest)',]:
    wtbl[colname].unit = u.mJy
for colname in ['$S_{peak}$(bsens)', '$S_{peak}$(cleanest)',]:
    wtbl[colname].unit = u.Jy


float_cols =  ['$\\theta_{maj}$',
 '$\\theta_{min}$',
 'BPA',
 '$S_{peak}$(bsens)',
 '$S_{peak}$(cleanest)',
 '$\\frac{S_{peak}(\mathrm{bsens})}{S_{peak}(\mathrm{cleanest})}$',
 '$\\sigma_{MAD}$(bsens)',
 '$\\sigma_{MAD}$(cleanest)',
 '$\\frac{\sigma_{MAD}(\mathrm{bsens})}{\sigma_{MAD}(\mathrm{cleanest})}$',
 'Requested $\sigma$',
 '$\sigma_{\mathrm{bsens}}/\sigma_{\mathrm{req}}$',
 '$f_{BW,cleanest}$',
 #'$\\theta_{req}$',
 #'\\sigma_{req}$',
 #'$\\sigma_{req}/\\sigma_{MAD}$',
 #'$\\theta_{req}/\\theta_{maj}$',
 #'DR$_{cleanest}$',
 #'DR$_{bsens}$',
 #'DR$_{bsens}$/DR$_{cleanest}$'
              ]

# convert to mJy
wtbl['$\sigma_{MAD}$(bsens)'] *= 1000
wtbl['$\sigma_{MAD}$(cleanest)'] *= 1000


formats = {key: lambda x: strip_trailing_zeros(('{0:0.3f}'.format(round_to_n(x,2))))
           for key in float_cols}


wtbl.write('bsens_cleanest_diff.ecsv', format='ascii.ecsv', overwrite=True)



# caption needs to be *before* preamble.
#latexdict['caption'] = 'Continuum Source IDs and photometry'
latexdict['header_start'] = '\label{tab:bsens_cleanest}'#\n\\footnotesize'
latexdict['preamble'] = '\caption{Best Sensitivity vs Cleanest Continuum comparison}\n\\resizebox{\\textwidth}{!}{'
latexdict['col_align'] = 'l'*len(wtbl.columns)
latexdict['tabletype'] = 'table*'
latexdict['tablefoot'] = ("}\par\n"
                          "Like Table \\ref{tab:selfcal}, but comparing the cleanest and bsens data.  "
                          "$\sigma_{MAD}$(bsens) and $\sigma_{MAD}$(cleanest) are the "
                          "standard deviation error estimates computed from a signal-free "
                          "region in the map using the Median Absolute Deviation as a "
                          "robust estimator.  Their ratio shows that the broader included "
                          "bandwidth increases sensitivity; $f_{BW,cleanest}$ specifies "
                          "the fraction of the total bandwidth that was incorporated into "
                          "the cleanest images.  "
                          "$S_{peak}$ is the peak intensity in the images."

                         )

wtbl.sort('Region')

wtbl.write("../datapaper/bsens_cleanest_diff.tex", formats=formats,
           overwrite=True, latexdict=latexdict)
