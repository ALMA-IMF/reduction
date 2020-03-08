from astropy.table import Table, Column
import requests
import keyring
from astropy import units as u

from latex_info import (latexdict, format_float, round_to_n, rounded,
                        rounded_arr, strip_trailing_zeros, exp_to_tex)

latexdict = latexdict.copy()

result = requests.get('https://bio.rc.ufl.edu/secure/adamginsburg/ALMA-IMF/October31Release/metadata_sc.ecsv',
             auth=('almaimf', keyring.get_password('almaimf', 'almaimf')))
with open('metadata_sc.ecsv', 'w') as fh:
    fh.write(result.text)

tbl = Table.read('metadata_sc.ecsv')

# downselect
keep = (tbl['suffix'] == 'finaliter') & (tbl['robust'] == 'r0.0') & (tbl['pbcor'])


wtbl = tbl[keep]


print(wtbl)

wtbl['selfcaliter'] = Column(data=[int(x[2:]) for x in wtbl['selfcaliter']])

cols_to_keep = {'region':'Region',
                'band':'Band',
                'selfcaliter':'$n_{sc}$',
                'bmaj':r'$\theta_{maj}$',
                'bmin':r'$\theta_{min}$',
                'bpa':'BPA',
                'peak':'$S_{peak}$',
                'mad':'$\sigma_{MAD}$',
                #'peak/mad': "DR",
                'Req_Res': r"$\theta_{req}$",
                'Req_Sens': r"\sigma_{req}$",
                'SensVsReq': r"$\sigma{req}$/\sigma_{MAD}$",
                'BeamVsReq': r"$\theta_{req}$/\theta_{maj}$",
                'dr_pre': "DR$_{pre}$",
                'dr_post': "DR$_{post}$",
                'dr_improvement': "DR$_{post}$/DR$_{pre}$"}

units = {'$S_{peak}$':u.mJy.to_string(u.format.LatexInline),
         '$\sigma_{MAD}$':u.mJy.to_string(u.format.LatexInline),
         '$\sigma_{req}$':u.mJy.to_string(u.format.LatexInline),
         r'$\theta_{req}$':u.arcsec.to_string(u.format.LatexInline),
         r'$\theta_{maj}$':u.arcsec.to_string(u.format.LatexInline),
         r'$\theta_{min}$':u.arcsec.to_string(u.format.LatexInline),
         r'PA':u.deg.to_string(u.format.LatexInline),
        }
latexdict['units'] = units

wtbl = wtbl[list(cols_to_keep.keys())]

for old, new in cols_to_keep.items():
    if old in wtbl.colnames:
        #wtbl[old].meta['description'] = description[old]
        wtbl.rename_column(old, new)
        if new in units:
            wtbl[new].unit = units[new]


formats = {key: lambda x: strip_trailing_zeros('{0:0.2f}'.format(round_to_n(x,2)))
           for key in cols_to_keep.values()}

wtbl.write('selfcal_summary.ecsv', format='ascii.ecsv', overwrite=True)



# caption needs to be *before* preamble.
#latexdict['caption'] = 'Continuum Source IDs and photometry'
latexdict['header_start'] = '\label{tab:selfcal}'#\n\\footnotesize'
latexdict['preamble'] = '\caption{Selfcal Summary}\n\\resizebox{\\textwidth}{!}{'
latexdict['col_align'] = 'l'*len(wtbl.columns)
latexdict['tabletype'] = 'table'
latexdict['tablefoot'] = ("}\par\n"
                          "Description"

                         )

wtbl.write(paths.texpath("selfcal_summary.tex"), formats=formats,
           overwrite=True, latexdict=latexdict)

