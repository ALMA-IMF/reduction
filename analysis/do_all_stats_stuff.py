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

assert 'SCRIPT_DIR' in os.environ
script_dir = Path(os.environ['SCRIPT_DIR'])

scripts = ['delivery_status.py',
           'imstats.py',
           'before_after_selfcal_quicklooks_Oct2020_release.py',
           'dirty_selfcal_compare.py',
           'bsens_comparison.py',
           'robust_comparisons.py',
           'selfcal_field_data.py',
           'continuum_selections.py',
           'cube_metadata_grid.py',
           'fullcube_quicklooks.py',
           '7m12m_comparison.py',
           'diagnostic_images.py',
           'diagnostic_spectra.py',
           'plot_uvspectra.py',
          ]

for scriptname in scripts:
    t0 = time.time()
    print(f"script={scriptname}, fullpath={script_dir / scriptname}")
    try:
        runpy.run_path(str(script_dir / scriptname), run_name="__main__")
    except Exception as ex:
        print(ex)
    pl.close('all')
    print(f"script {scriptname} took {(time.time() - t0)/3600.:0.1f} hours")


# run locally runpy.run_path('latex_table.py', run_name="__main__")
#runpy.run_path('before_after_selfcal_quicklooks_July2020_release.py', run_name="__main__")
#runpy.run_path('before_after_selfcal_quicklooks_Feb2020_release.py', run_name="__main__")
#runpy.run_path('before_after_selfcal_quicklooks_October31_2019_release.py', run_name="__main__")
#runpy.run_path('compare_to_auto.py', run_name="__main__")
