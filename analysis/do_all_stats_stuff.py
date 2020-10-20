"""
Run all of the summary statistics
"""
import runpy
import pylab as pl
import os

script_dir = os.environ['SCRIPT_DIR']
os.chdir(script_dir)

scripts = ['delivery_status.py',
           'imstats.py',
           'before_after_selfcal_quicklooks_October2020_release.py',
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
    print(scriptname)
    try:
        runpy.run_path(scriptname, run_name="__main__")
    except Exception as ex:
        print(ex)
    pl.close('all')


# run locally runpy.run_path('latex_table.py', run_name="__main__")
#runpy.run_path('before_after_selfcal_quicklooks_July2020_release.py', run_name="__main__")
#runpy.run_path('before_after_selfcal_quicklooks_Feb2020_release.py', run_name="__main__")
#runpy.run_path('before_after_selfcal_quicklooks_October31_2019_release.py', run_name="__main__")
#runpy.run_path('compare_to_auto.py', run_name="__main__")
