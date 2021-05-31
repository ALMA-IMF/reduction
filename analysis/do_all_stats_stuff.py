"""
Run all of the summary statistics
"""
import runpy
import matplotlib
matplotlib.use('agg')
import pylab as pl
import os
import time
from pathlib import Path
from astropy import log

assert 'SCRIPT_DIR' in os.environ
script_dir = Path(os.environ['SCRIPT_DIR'])

scripts = [
           'make_june2021release.py',
           #'make_may2021release.py',
           #'make_oct2020release.py',
           # don't do this any more 'link_files.py',
           'link_files_restructured.py',
           'delivery_status.py',
           'imstats.py',
           #'before_after_selfcal_quicklooks_Feb2021release.py',
           #'before_after_selfcal_quicklooks_May2021release.py',
           'before_after_selfcal_quicklooks_June2021release.py',
           'compare_June2021_to_May2021.py',
           'bsens_comparison.py',
           'bsens_cleanest_diff_zooms.py',
           'psf_check_figures.py',
           'continuum_selections.py',
           'central_frequency.py',
           'dirty_selfcal_compare.py',
           'robust_comparisons.py',
           'selfcal_field_data.py',
           'cube_metadata_grid.py',
           'cube_spectral_quicklooks.py',
           # this is a library, not a script: 'diagnostic_images.py',
           'diagnostic_spectra.py',
           'plot_uvspectra.py',
           'fullcube_quicklooks.py',
           '7m12m_comparison.py',
           'cube_stats_grid.py',
          ]

for scriptname in scripts:
    t0 = time.time()
    log.info(f"script={scriptname}, fullpath={script_dir / scriptname}")
    print(f"script={scriptname}, fullpath={script_dir / scriptname}")
    try:
        runpy.run_path(str(script_dir / scriptname), run_name="__main__")
    except Exception as ex:
        print("Exception: ",ex)
    pl.close('all')
    log.info(f"script {scriptname} took {(time.time() - t0)/3600.:0.1f} hours")
    print(f"script {scriptname} took {(time.time() - t0)/3600.:0.1f} hours")


# run locally runpy.run_path('latex_table.py', run_name="__main__")
#runpy.run_path('before_after_selfcal_quicklooks_July2020_release.py', run_name="__main__")
#runpy.run_path('before_after_selfcal_quicklooks_Feb2020_release.py', run_name="__main__")
#runpy.run_path('before_after_selfcal_quicklooks_October31_2019_release.py', run_name="__main__")
#runpy.run_path('compare_to_auto.py', run_name="__main__")
