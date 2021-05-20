import numpy as np
from astropy.table import Table, Column
from astropy import table
import requests
import keyring
import datetime
from astropy import units as u

from latex_info import (latexdict, format_float, round_to_n, rounded,
                        rounded_arr, strip_trailing_zeros, exp_to_tex)

latexdict = latexdict.copy()

if datetime.datetime.today() > datetime.datetime(year=2021, month=1, day=10):
    result = requests.get('https://data.rc.ufl.edu/secure/adamginsburg/ALMA-IMF/February2021Release/tables/metadata_sc.ecsv',
                          auth=('almaimf', keyring.get_password('almaimf', 'almaimf')))
    with open('metadata_sc.ecsv', 'w') as fh:
        fh.write(result.text)

    result = requests.get('https://data.rc.ufl.edu/secure/adamginsburg/ALMA-IMF/tables/bandpass_fraction.ecsv',
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

tbl = table.join(Table.read('metadata_sc.ecsv'), bp_tbl, keys=('region', 'band'))
bad = np.array(['diff' in x for x in tbl['filename']])

# downselect
keep = ((tbl['suffix'] == 'finaliter') &
        (tbl['robust'] == 'r0.0') &
        (~tbl['pbcor']) &
        (~tbl['bsens']) &
        (~bad))


wtbl = tbl[keep]


print(len(wtbl))
print(wtbl)

# strip preceding "sc" from selfcal numbers
wtbl['selfcaliter'] = Column(data=[row['selfcaliter'][2:]+("a" if row['has_amp'] else "") for row in wtbl])

# SensVsReq can be populated with either pre- or post-; we want post
wtbl['SensVsReqPost'] = wtbl['mad_sample_post'] / wtbl['Req_Sens']
wtbl['SensVsReqPre'] = wtbl['mad_sample_pre'] / wtbl['Req_Sens']

cols_to_keep = {'region':'Region',
                'band':'Band',
                'selfcaliter':'$n_{sc}$',
                'bmaj':r'$\theta_{maj}$',
                'bmin':r'$\theta_{min}$',
                'bpa':'BPA',
                'Req_Res': r"$\theta_{req}$",
                'BeamVsReq': r"$\Omega_{syn}^{1/2}/\Omega_{req}^{1/2}$",
                #'peak/mad': "DR",
                'peak':'$S_{peak}$',
                'mad':'$\sigma_{MAD}$',
                'Req_Sens': r"$\sigma_{req}$",
                'SensVsReqPost': r"$\sigma_{MAD}/\sigma_{req}$",
                'dr_pre': "DR$_{pre}$",
                'dr_post': "DR$_{post}$",
                'dr_improvement': "DR$_{post}$/DR$_{pre}$"}

units = {'$S_{peak}$':(u.Jy/u.beam).to_string(u.format.LatexInline),
         '$\sigma_{MAD}$':(u.mJy/u.beam).to_string(u.format.LatexInline),
         '$\sigma_{req}$':(u.mJy/u.beam).to_string(u.format.LatexInline),
         r'$\theta_{req}$':u.arcsec.to_string(u.format.LatexInline),
         r'$\theta_{maj}$':u.arcsec.to_string(u.format.LatexInline),
         r'$\theta_{min}$':u.arcsec.to_string(u.format.LatexInline),
         r'PA':u.deg.to_string(u.format.LatexInline),
        }
latexdict['units'] = units

fwtbl = wtbl[list(cols_to_keep.keys())]


for old, new in cols_to_keep.items():
    if old in wtbl.colnames:
        #wtbl[old].meta['description'] = description[old]
        fwtbl.rename_column(old, new)
        if new in units:
            fwtbl[new].unit = units[new]

float_cols =  ['$\\theta_{maj}$',
 '$\\theta_{min}$',
 'BPA',
 '$S_{peak}$',
 '$\\sigma_{MAD}$',
 '$\\theta_{req}$',
 '\\sigma_{req}$',
 '$\\sigma_{MAD}/\\sigma_{req}$',
# '$\\theta_{req}/\\theta_{maj}$',
 "$\Omega_{syn}^{1/2}/\Omega_{req}^{1/2}$",
 'DR$_{pre}$',
 'DR$_{post}$',
 'DR$_{post}$/DR$_{pre}$']

# convert to mJy
fwtbl['$\sigma_{MAD}$'] *= 1000


formats = {key: lambda x: strip_trailing_zeros('{0:0.3f}'.format(round_to_n(x,2)))
           for key in float_cols}

fwtbl.write('selfcal_summary.ecsv', format='ascii.ecsv', overwrite=True)



# caption needs to be *before* preamble.
#latexdict['caption'] = 'Continuum Source IDs and photometry'
latexdict['header_start'] = '\label{tab:selfcal}'#\n\\footnotesize'
latexdict['preamble'] = '\caption{Selfcal Summary}\n\\resizebox{\\textwidth}{!}{'
latexdict['col_align'] = 'l'*len(fwtbl.columns)
latexdict['tabletype'] = 'table*'
latexdict['tablefoot'] = ("}\par\n"
                          "$n_{sc}$ is the number of self-calibration iterations adopted.  "
                          "Those with a final iteration of amplitude self-calibration are denoted with the `a' suffix.  "
                          "$\\theta_{maj}, \\theta_{min}$, and BPA give the major and minor full-width-half-maxima (FWHM) of the synthesized beams.  "
                          "$\\theta_{req}$ is the requested beam size, "
                          "and $\\Omega_{syn}^{1/2}/\\Omega_{req}^{1/2}$ gives the ratio of the synthesized to the "
                          "requested beam area; larger numbers imply poorer resolution.  "
                          "$\sigma_{MAD}$ and $\sigma_{req}$ are the measured and requested "
                          "RMS sensitivity, respectively, and $\sigma_{MAD}/\sigma_{req}$ is the excess noise "
                          "in the image over that requested.  $\sigma_{MAD}$ is measured on the \\texttt{cleanest} images.  "
                          "$DR_{pre}$ and $DR_{post}$ are the dynamic range, $S_{peak} / \sigma_{MAD}$, for the "
                          "pre- and post-self-calibration data; $DR_{post}/DR_{pre}$ gives the improvement "
                          "factor."
                         )

fwtbl.sort('Band')
fwtbl.sort('Region')

fwtbl.write("../datapaper/selfcal_summary.tex", formats=formats,
           overwrite=True, latexdict=latexdict)

