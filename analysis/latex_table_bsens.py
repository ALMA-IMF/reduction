import numpy as np
from astropy.table import Table, Column
from astropy import table
import requests
import keyring
from astropy import units as u
import datetime
import sigfig

from latex_info import (latexdict, format_float, round_to_n, rounded,
                        rounded_arr, strip_trailing_zeros, exp_to_tex)

latexdict = latexdict.copy()

def make_latex_table(releasename='February2021', savename='bsens_cleanest_diff'):
    if datetime.datetime.today() > datetime.datetime(year=2021, month=1, day=10):
        result = requests.get(f'https://bio.rc.ufl.edu/secure/adamginsburg/ALMA-IMF/{releasename}Release/tables/metadata_bsens_cleanest.ecsv',
                              auth=('almaimf', keyring.get_password('almaimf', 'almaimf')))
        with open(f'{releasename}_metadata_bsens_cleanest.ecsv', 'w') as fh:
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

    tbl = table.join(Table.read(f'{releasename}_metadata_bsens_cleanest.ecsv'), bp_tbl, keys=('region', 'band'))
    bad = np.array(['diff' in x for x in tbl['filename']])

    # downselect (need bsens=true to avoid duplication - but be wary in case you remove duplicates upstream!)
    keep = ((tbl['suffix'] == 'finaliter') &
            (tbl['robust'] == 'r0.0') &
            (~tbl['pbcor']) &
            (tbl['bsens']) &
            (~tbl['nobright']) &
            (~bad))


    wtbl = tbl[keep]


    print(len(wtbl))
    print(wtbl)

    wtbl['selfcaliter'] = Column(data=[int(x[2:]) for x in wtbl['selfcaliter']])
    wtbl['bsens_div_cleanest_mad'] = wtbl['mad_sample_bsens'] / wtbl['mad_sample_cleanest']
    wtbl['bsens_div_cleanest_max'] = wtbl['max_bsens'] / wtbl['max_cleanest']
    wtbl['bsens_mad_div_req'] = wtbl['mad_sample_bsens'] / wtbl['Req_Sens']# * 1e3

    wtbl['max_bsens'].unit = u.mJy/u.beam
    wtbl['max_cleanest'].unit = u.mJy/u.beam

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
                    'mad_sample_bsens':'$\sigma_{MAD}$(bsens)',
                    'mad_sample_cleanest':'$\sigma_{MAD}$(cleanest)',
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


    units = {'$S_{peak}(bsens)$':(u.mJy/u.beam).to_string(u.format.LatexInline),
             '$S_{peak}(cleanest)$':(u.mJy/u.beam).to_string(u.format.LatexInline),
             '$\sigma_{MAD}(bsens)$':(u.mJy/u.beam).to_string(u.format.LatexInline),
             '$\sigma_{MAD}(cleanest)$':(u.mJy/u.beam).to_string(u.format.LatexInline),
             'Requested $\sigma$':(u.mJy/u.beam).to_string(u.format.LatexInline),
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
        wtbl[colname].unit = u.mJy/u.beam
    for colname in ['$S_{peak}$(bsens)', '$S_{peak}$(cleanest)',]:
        wtbl[colname].unit = u.mJy/u.beam


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
    # wtbl['$\sigma_{MAD}$(bsens)'] *= 1000
    # wtbl['$\sigma_{MAD}$(cleanest)'] *= 1000


    formats = {key: lambda x: strip_trailing_zeros(('{0:0.3f}'.format(round_to_n(x,2))))
               for key in float_cols}
    formats = {key: lambda x: str(sigfig.round(str(x), sigfigs=2))
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

    wtbl.sort(['Region','Band'])

    wtbl.write(f"../datapaper/{savename}.tex", formats=formats,
               overwrite=True, latexdict=latexdict)

    return wtbl


FOV = {
('G008.67', 'B3'): r"190$\times$125",
('G008.67', 'B6'): r"132$\times$87",
('G010.62', 'B3'): r"$150\times160$",
('G010.62', 'B6'): r"$98\times90$",
('G012.80', 'B3'): r"$190\times180$",
('G012.80', 'B6'): r"$132\times132$",
('G327.29', 'B3'): r"$160\times152$",
('G327.29', 'B6'): r"$105\times109$",
('G328.25', 'B3'): r"$160\times180$",
('G328.25', 'B6'): r"$120\times120$",
('G333.60', 'B3'): r"$190\times180$",
('G333.60', 'B6'): r"$143\times143$",
('G337.92', 'B3'): r"$160\times152$",
('G337.92', 'B6'): r"$92\times86$",
('G338.93', 'B3'): r"$152\times160$",
('G338.93', 'B6'): r"$86\times92$",
('G351.77', 'B3'): r"$190\times180$",
('G351.77', 'B6'): r"$132\times132$",
('G353.41', 'B3'): r"$190\times180$",
('G353.41', 'B6'): r"$131\times131$",
('W43-MM1', 'B3'): r"$190\times150$",
('W43-MM1', 'B6'): r"$117\times53$",
('W43-MM2', 'B3'): r"$190\times150$",
('W43-MM2', 'B6'): r"$90\times98$",
('W43-MM3', 'B3'): r"$190\times150$",
('W43-MM3', 'B6'): r"$100\times90$",
('W51-E',   'B3'): r"$150\times160$",
('W51-E',   'B6'): r"$100\times90$",
('W51-IRS2','B3'): r"$160\times150$",
('W51-IRS2','B6'): r"$92\times98$",
      }

def make_latex_table_overview(releasename='June2021', savename='res_sens'):
    if datetime.datetime.today() > datetime.datetime(year=2021, month=1, day=10):
        result = requests.get(f'https://bio.rc.ufl.edu/secure/adamginsburg/ALMA-IMF/{releasename}Release/tables/metadata_bsens_cleanest.ecsv',
                              auth=('almaimf', keyring.get_password('almaimf', 'almaimf')))
        with open(f'{releasename}_metadata_bsens_cleanest.ecsv', 'w') as fh:
            fh.write(result.text)


        result = requests.get('https://bio.rc.ufl.edu/secure/adamginsburg/ALMA-IMF/tables/bandpass_fraction.ecsv',
                              auth=('almaimf', keyring.get_password('almaimf', 'almaimf')))
        with open('bandpass_fraction.ecsv', 'w') as fh:
            fh.write(result.text)

    result = requests.get('https://data.rc.ufl.edu/secure/adamginsburg/ALMA-IMF/May2021Release/tables/uvspacings.ecsv',
                              auth=('almaimf', keyring.get_password('almaimf', 'almaimf')))
    with open('uvspacings.ecsv', 'w') as fh:
        fh.write(result.text)


    bp_tbl = Table.read('bandpass_fraction.ecsv')
    bp_tbl['band'] = [f'B{b}' for b in bp_tbl['band']]
    bp_tbl.rename_column('field','region')
    bp_tbl = table.join(bp_tbl.group_by('config').groups[0], bp_tbl.group_by('config').groups[1], keys=('region', 'band'))
    bp_tbl.rename_column('bwfrac_1', '12Mlong_frac')
    bp_tbl.rename_column('bwfrac_2', '12Mshort_frac')
    bp_tbl.remove_column('config_1')
    bp_tbl.remove_column('config_2')

    uvtbl = Table.read('uvspacings.ecsv')

    tbl = table.join(Table.read(f'{releasename}_metadata_bsens_cleanest.ecsv'), bp_tbl, keys=('region', 'band'))
    tbl = table.join(tbl, uvtbl)
    bad = np.array(['diff' in x for x in tbl['filename']])

    # downselect (need bsens=true to avoid duplication - but be wary in case you remove duplicates upstream!)
    keep = ((tbl['suffix'] == 'finaliter') &
            (tbl['robust'] == 'r0.0') &
            (~tbl['pbcor']) &
            (tbl['bsens']) &
            (~tbl['nobright']) &
            (~bad))


    wtbl = tbl[keep]


    print(len(wtbl))
    print(wtbl)

    wtbl['selfcaliter'] = Column(data=[int(x[2:]) for x in wtbl['selfcaliter']])
    wtbl['bsens_div_cleanest_mad'] = wtbl['mad_sample_bsens'] / wtbl['mad_sample_cleanest']
    wtbl['bsens_div_cleanest_max'] = wtbl['max_bsens'] / wtbl['max_cleanest']
    wtbl['bsens_mad_div_req'] = wtbl['mad_sample_bsens'] / wtbl['Req_Sens']# * 1e3

    wtbl['max_bsens'].unit = u.mJy/u.beam
    wtbl['max_cleanest'].unit = u.mJy/u.beam

    cols_to_keep = {'region':'Region', 'FOV_B3': 'FOV(B3)', 'FOV_B6': 'FOV(B6)'}

    for band in ('B3', 'B6'):
        cols_to_keep[f'bmaj_{band}'] = f'$\\theta_{{maj}}({band})$'
        cols_to_keep[f'bmin_{band}'] = f'$\\theta_{{min}}({band})$'
        cols_to_keep[f'mad_sample_bsens_{band}'] = f'$\sigma_{{MAD}}$(bsens,{band})'
        cols_to_keep[f'mad_sample_cleanest_{band}'] = f'$\sigma_{{MAD}}$(cleanest,{band})'
        cols_to_keep[f'10%_{band}'] = f'LAS$_{{10\%}}$({band})'


    # Region &
    # FOV$_{B6}$ &	$\theta_{maj}\times\theta_{min}(B6)$ &	 $\sigma_{MAD}(cleanest)$ & $\sigma_{MAD}(bsens)$   & LAS(5\%, B6) &
    # FOV$_{B3}$ &	$\theta_{maj}\times\theta_{min}(B3)$ &	 $\sigma_{MAD}(cleanest)$ & $\sigma_{MAD}(bsens)$   & LAS(5\%, B3) \\

    cols = ['bmaj', 'bmin', '10%', 'mad_sample_bsens', 'mad_sample_cleanest']

    wtbl.add_index('region')
    wtbl.add_index('band')
    rows = []
    for region in set(wtbl['region']):
        row = {f'{key}_{band}': wtbl.loc['band', band].loc['region', region][key]
               for key in cols
               for band in ('B3', 'B6')}
        row['region'] = region
        row['FOV_B3'] = FOV[(region, 'B3')]
        row['FOV_B6'] = FOV[(region, 'B6')]
        rows.append(row)

    mtbl = Table(rows)


    units = {'$S_{peak}(bsens)$':(u.mJy/u.beam).to_string(u.format.LatexInline),
             '$S_{peak}(cleanest)$':(u.mJy/u.beam).to_string(u.format.LatexInline),
             '$\sigma_{MAD}(bsens,B6)$':(u.mJy/u.beam).to_string(u.format.LatexInline),
             '$\sigma_{MAD}(cleanes,B6)$':(u.mJy/u.beam).to_string(u.format.LatexInline),
             '$\sigma_{MAD}(bsens,B3)$':(u.mJy/u.beam).to_string(u.format.LatexInline),
             '$\sigma_{MAD}(cleanest,B3)$':(u.mJy/u.beam).to_string(u.format.LatexInline),
             #'$\sigma_{req}$':u.mJy.to_string(u.format.LatexInline),
             #r'$\theta_{req}$':u.arcsec.to_string(u.format.LatexInline),
             r'$\theta_{maj}(B3)$':u.arcsec.to_string(u.format.LatexInline),
             r'$\theta_{min}(B3)$':u.arcsec.to_string(u.format.LatexInline),
             r'$\theta_{maj}(B6)$':u.arcsec.to_string(u.format.LatexInline),
             r'$\theta_{min}(B6)$':u.arcsec.to_string(u.format.LatexInline),
             'LAS$_{10\%}$(B3)$':u.arcsec.to_string(u.format.LatexInline),
             'LAS$_{10\%}$(B6)$':u.arcsec.to_string(u.format.LatexInline),
             #r'PA':u.deg.to_string(u.format.LatexInline),
            }
    latexdict['units'] = units

    mtbl.add_column(col=[f'${major:0.2f}\\times{minor:0.2f}$' for major,minor in zip(mtbl['bmaj_B3'], mtbl['bmin_B3'])], name='Res. B3')
    mtbl.add_column(col=[f'${major:0.2f}\\times{minor:0.2f}$' for major,minor in zip(mtbl['bmaj_B6'], mtbl['bmin_B6'])], name='Res. B6')

    column_order = ['region', ]
    for band in ('B3','B6'):
        column_order += [f'FOV_{band}', f'Res. {band}', f'mad_sample_cleanest_{band}', f'mad_sample_bsens_{band}', f'10%_{band}']

    mtbl = mtbl[column_order]


    for old, new in cols_to_keep.items():
        if old in mtbl.colnames:
            #mtbl[old].meta['description'] = description[old]
            mtbl.rename_column(old, new)
            if new in units:
                mtbl[new].unit = units[new]

    for colname in ['$\sigma_{MAD}$(bsens,B3)', '$\sigma_{MAD}$(cleanest,B3)',
                    '$\sigma_{MAD}$(bsens,B6)', '$\sigma_{MAD}$(cleanest,B6)',
                   ]:
        mtbl[colname].unit = u.mJy/u.beam

    for colname in ('FOV(B3)', 'FOV(B6)', 'Res. B3', 'Res. B6'):
        mtbl[colname].unit = u.arcsec


    float_cols =  [
     '$\\theta_{maj}(B3)$',
     '$\\theta_{min}(B3)$',
     '$\\theta_{maj}(B6)$',
     '$\\theta_{min}(B6)$',
     'LAS$_{10\%}$(B3)',
     'LAS$_{10\%}$(B6)',
     'BPA',
     '$S_{peak}$(bsens)',
     '$S_{peak}$(cleanest)',
     '$\\frac{S_{peak}(\mathrm{bsens})}{S_{peak}(\mathrm{cleanest})}$',
     '$\\sigma_{MAD}$(bsens,B3)',
     '$\\sigma_{MAD}$(cleanest,B3)',
     '$\\sigma_{MAD}$(bsens,B6)',
     '$\\sigma_{MAD}$(cleanest,B6)',
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
    # mtbl['$\sigma_{MAD}$(bsens)'] *= 1000
    # mtbl['$\sigma_{MAD}$(cleanest)'] *= 1000


    formats = {key: lambda x: strip_trailing_zeros(('{0:0.3f}'.format(round_to_n(x,2))))
               for key in float_cols}
    formats = {key: lambda x: str(sigfig.round(str(x), sigfigs=2))
               for key in float_cols}


    mtbl.write('overviewpapertble.ecsv', format='ascii.ecsv', overwrite=True)



    # caption needs to be *before* preamble.
    #latexdict['caption'] = 'Continuum Source IDs and photometry'
    latexdict['header_start'] = ('\label{tab:sensitivity_scale_overview}\n\n'
                                 ' & \multicolumn{5}{c}{B3} & \multicolumn{5}{c}{B6}\\\\')
    latexdict['preamble'] = '\caption{Overview of sensitivity and angular scales}\n\\resizebox{\\textwidth}{!}{'
    latexdict['col_align'] = 'l|lllll|lllll|'
    latexdict['tabletype'] = 'table*'
    latexdict['tablefoot'] = ("}\par\n"
                              ""

                             )

    mtbl.sort(['Region'])

    mtbl.write(f"../overviewpaper/tables/{savename}.tex", formats=formats,
               overwrite=True, latexdict=latexdict)

    with open(f"../overviewpaper/tables/{savename}.tex", 'r') as fh:
        lines = fh.readlines()
    with open(f"../overviewpaper/tables/{savename}.tex", 'w') as fh:
        for row in lines:
            if 'FOV(B3)' in row:
                row = row.replace('(B3)','').replace('(B6)','').replace(',B3','').replace(',B6','').replace(" B3","").replace(" B6","")
            fh.write(row)

    return mtbl



if __name__ == "__main__":

    feb_bs = make_latex_table(releasename='February2021', savename='bsens_cleanest_diff')
    jun_bs = make_latex_table(releasename='June2021', savename='bsens_cleanest_diff_June2021')
    ovtbl = make_latex_table_overview()
