import glob
from make_selfcal_animation import make_anim, make_anim_single
import os
import shutil

os.chdir('/orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/')

for fn in glob.glob("*_12M_robust0_*finaliter*.image.tt0.fits"):
    imname = fn.split("_selfcal")[0]
    print(imname)
    make_anim(imname)
    make_anim_single(imname, 'image')

    shutil.copy(f'{imname}_selfcal_anim.gif', '/bio/web/secure/adamginsburg/ALMA-IMF/October2020Release/selfcal_animations/')
    #shutil.copy(f'{imname}_image_selfcal_anim.gif', '/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/selfcal_animations/')
