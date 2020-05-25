"""
Run all of the summary statistics

October 31 (2019) stuff can be commented out later
"""
import runpy
import pylab as pl
runpy.run_path('imstats.py', run_name="__main__")
runpy.run_path('before_after_selfcal_quicklooks_Feb2020_release.py', run_name="__main__")
pl.close('all')
runpy.run_path('dirty_selfcal_compare.py', run_name="__main__")
pl.close('all')
runpy.run_path('7m12m_comparison.py', run_name="__main__")
pl.close('all')
runpy.run_path('bsens_comparison.py', run_name="__main__")
pl.close('all')
runpy.run_path('selfcal_field_data.py', run_name="__main__")
pl.close('all')
# run locall runpy.run_path('latex_table.py', run_name="__main__")
runpy.run_path('compare_to_auto.py', run_name="__main__")
pl.close('all')
runpy.run_path('before_after_selfcal_quicklooks_October31_2019_release.py', run_name="__main__")
