import numpy as np
from astropy.table import Table, Column
from astropy import table
import requests
import keyring
import datetime
from astropy import units as u
import sigfig

from latex_info import (latexdict, format_float, round_to_n, rounded,
                        rounded_arr, strip_trailing_zeros, exp_to_tex)

latexdict = latexdict.copy()

import sys
sys.path.append('../reduction')
from imaging_parameters import selfcal_pars

pars = {key: selfcal_pars[key] for key in selfcal_pars if '_12M_robust0' in key and 'robust0.5' not in key and 'bsens' not in key}


datatable = {'field': [],
             'band': [],
             'niter': [],
             'gaintypes': [],
             'calmodes': [],
             'solints': []}

for key,entry in sorted(pars.items()):
    field = key.split("_")[0]
    band = key.split("_")[1]
    niter = len(entry)
    gaintypes = ','.join([ee['gaintype'] for _,ee in sorted(entry.items())])
    calmodes = ','.join([ee['calmode'] for _,ee in sorted(entry.items())])
    solints = ','.join([ee['solint'] for _,ee in sorted(entry.items())])

    datatable['field'].append(field)
    datatable['band'].append(band)
    datatable['niter'].append(niter)
    datatable['gaintypes'].append(gaintypes)
    datatable['calmodes'].append(calmodes)
    datatable['solints'].append(solints)

tbl = Table(datatable)

tbl.rename_column('field', 'Field')
tbl.rename_column('band', 'Band')
tbl.rename_column('niter', '$N_{iter}$')
tbl.rename_column('gaintypes', 'Gaintypes')
tbl.rename_column('calmodes', 'Cal. Modes')
tbl.rename_column('solints', 'Solution Intervals')


latexdict['header_start'] = '\label{tab:selfcaldetails}'#\n\\footnotesize'
latexdict['preamble'] = '\caption{Selfcal Details}\n\\resizebox{\\textwidth}{!}{'
latexdict['col_align'] = 'l'*len(tbl.columns)
latexdict['tabletype'] = 'table*'
latexdict['tablefoot'] = "}\par The comma-separated lists give the parameters, in order, for each iteration of self-calibration.\n"

tbl.write("../datapaper/selfcaldetails.tex", latexdict=latexdict, overwrite=True)
