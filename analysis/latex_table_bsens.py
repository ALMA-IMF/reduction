from astropy.table import Table, Column
import requests
import keyring
from astropy import units as u

from latex_info import (latexdict, format_float, round_to_n, rounded,
                        rounded_arr, strip_trailing_zeros, exp_to_tex)

latexdict = latexdict.copy()

result = requests.get('https://bio.rc.ufl.edu/secure/adamginsburg/ALMA-IMF/Feb2020/metadata_bsens_cleanest.ecsv',
                      auth=('almaimf', keyring.get_password('almaimf', 'almaimf')))
with open('metadata_bsens_cleanest.ecsv', 'w') as fh:
    fh.write(result.text)

tbl = Table.read('metadata_bsens_cleanest.ecsv')

# downselect (need bsens=true to avoid duplication - but be wary in case you remove duplicates upstream!)
keep = (tbl['suffix'] == 'finaliter') & (tbl['robust'] == 'r0.0') & (tbl['pbcor']) & (tbl['bsens'])


wtbl = tbl[keep]


print(wtbl)

wtbl['selfcaliter'] = Column(data=[int(x[2:]) for x in wtbl['selfcaliter']])
wtbl['bsens_div_cleanest_mad'] = wtbl['mad_bsens'] / wtbl['mad_cleanest']
wtbl['bsens_div_cleanest_max'] = wtbl['max_bsens'] / wtbl['max_cleanest']


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
                'bsens_div_cleanest_mad':'$\sigma_{MAD}$(bsens)/$\sigma_{MAD}$(cleanest)',
                'max_bsens':'$S_{peak}$(bsens)',
                'max_cleanest':'$S_{peak}$(cleanest)',
                'bsens_div_cleanest_max':'$S_{peak}$(bsens)/$S_{peak}$(cleanest)',
                #'dr_cleanest': "DR$_{cleanest}$",
                #'dr_bsens': "DR$_{bsens}$",
               }


units = {'$S_{peak}(bsens)$':u.Jy.to_string(u.format.LatexInline),
         '$S_{peak}(cleanest)$':u.Jy.to_string(u.format.LatexInline),
         '$\sigma_{MAD}(bsens)$':u.mJy.to_string(u.format.LatexInline),
         '$\sigma_{MAD}(cleanest)$':u.mJy.to_string(u.format.LatexInline),
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
 '$S_{peak}$(bsens)/$S_{peak}$(cleanest)',
 '$\\sigma_{MAD}$(bsens)',
 '$\\sigma_{MAD}$(cleanest)',
 '$\sigma_{MAD}$(bsens)/$\sigma_{MAD}$(cleanest)',
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


formats = {key: lambda x: strip_trailing_zeros('{0:0.2f}'.format(round_to_n(x,2)))
           for key in float_cols}


wtbl.write('bsens_cleanest_diff.ecsv', format='ascii.ecsv', overwrite=True)



# caption needs to be *before* preamble.
#latexdict['caption'] = 'Continuum Source IDs and photometry'
latexdict['header_start'] = '\label{tab:bsens_cleanest}'#\n\\footnotesize'
latexdict['preamble'] = '\caption{Best Sensitivity vs Cleanest Continuum comparison}\n\\resizebox{\\textwidth}{!}{'
latexdict['col_align'] = 'l'*len(wtbl.columns)
latexdict['tabletype'] = 'table'
latexdict['tablefoot'] = ("}\par\n"
                          "Description"

                         )

wtbl.sort('Region')

wtbl.write("../datapaper/bsens_cleanest_diff.tex", formats=formats,
           overwrite=True, latexdict=latexdict)
