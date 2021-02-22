import shutil
from pathlib import Path
from astropy.io import fits

README_TEMPLATE = """
The files included in this delivery (May 25, 2020) have not undergone final
quality assessment.  Please go to
https://bio.rc.ufl.edu/secure/adamginsburg/ALMA-IMF/May2020/quicklooks/index.html
to contribute to the quality assessment.  These files may be the final product
if they pass QA, but if serious issues are noted, a new version will be
produced.

The pipeline version used to produce these images is: {pipeline_version} from {pipeline_date}
The CASA version used to produce these images is: {casa_version}

Files include:
*.image.tt0.pbcor.fits
*.image.tt0.fits

The list of additional files available upon request, but not reviewed by the data team, is below:
{extra_files}
"""

if __name__ == "__main__":
    basepath = Path('/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/Feb2020/')
    targetpath = Path('/orange/adamginsburg/web/secure/adamginsburg/ALMA-IMF/May2020/')

    import os
    for root, dirs, files in os.walk(basepath):
        rootpath = Path(root)
        if (root.endswith('bsens') or root.endswith('cleanest')) and '7m12m' not in root:
            extra_files = []
            for name in files:
                if 'finaliter' in name and (name.endswith('image.tt0.pbcor.fits') or name.endswith('image.tt0.fits')):
                    rel_dir = Path(root.split(str(basepath))[-1].lstrip("/"))
                    savepath = targetpath / rel_dir
                    savepath.mkdir(parents=True, exist_ok=True)
                    fpath = Path(name)
                    shutil.copy(rootpath / fpath, savepath / fpath)
                    header = fits.getheader(rootpath / fpath)
                else:
                    extra_files.append(name)
            with open(savepath / Path('README'), 'w') as fh:
                fh.write(README_TEMPLATE.format(extra_files='\n'.join(extra_files),
                                                pipeline_version=header['GIT_VERS'] if 'GIT_VERS' in header else 'Unknown',
                                                pipeline_date=header['GIT_DATE'] if 'GIT_DATE' in header else 'Unknown',
                                                casa_version=header['ORIGIN'],
                                               ))
        else:
            continue
