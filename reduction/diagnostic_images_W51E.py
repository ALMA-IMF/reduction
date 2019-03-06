import pylab as pl
from diagnostic_images import load_images, show

imgs_before_b6, cubes_before_b6 = load_images('W51-E_B6_uid___A001_X1296_X215_continuum_merged_12M_robust0')
imgs_after_b6, cubes_after_b6 = load_images('W51-E_B6_uid___A001_X1296_X215_continuum_merged_12M_robust0_selfcal1')

show(imgs_before_b6, vmin=-0.001, vmax=0.01)
pl.savefig("W51-E_B6_before_selfcal.png", bbox_inches='tight')

show(imgs_after_b6, vmin=-0.001, vmax=0.01)
pl.savefig("W51-E_B6_after_selfcal.png", bbox_inches='tight')


show(imgs_before_b6, vmin=-0.001, vmax=0.3, zoom=[slice(380,900), slice(480,760)])
pl.savefig("W51-E_B6_before_selfcal_zoom.png", bbox_inches='tight')

show(imgs_after_b6, vmin=-0.001, vmax=0.3, zoom=[slice(380,900), slice(480,760)])
pl.savefig("W51-E_B6_after_selfcal_zoom.png", bbox_inches='tight')


imgs_before_b3, cubes_before_b3 = load_images('W51-E_B3_uid___A001_X1296_X10b_continuum_merged_12M_robust0')
show(imgs_before_b3, vmin=-0.001, vmax=0.01)
pl.savefig("W51-E_B3_before_selfcal.png", bbox_inches='tight')

show(imgs_before_b3, vmin=-0.001, vmax=0.01, zoom=[slice(680,1200),slice(850,1200)])
pl.savefig("W51-E_B3_before_selfcal_zoom.png", bbox_inches='tight')
