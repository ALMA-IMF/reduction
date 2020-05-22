from astropy.io import fits

KEYWORDS = ["niter", "deconvolver", "scales", "pblimit", "weighting", "specmode", "nterms", "threshold", "robust", "gridder", "git_version", "git_date",]

def has_history(filename):

    header = fits.getheader(filename)

    if 'HISTORY' not in header:
        return False

    history = header['HISTORY']

    OK = set()

    for row in history:
        key = row.split(": ")[0]
        if key in KEYWORDS:
            OK = OK | {key}

    if len(OK) > 2:
        return True
    else:
        return False

def update_header_from_history(filename):

    fh = fits.open(filename, mode='update')

    header = fh[0].header

    update_keywords = {}

    for row in header['HISTORY']:
        key = row.split(": ")[0]
        if key in KEYWORDS:
            value = row.split(key+": ")[1]
            update_keywords[key[:8]] = value

    for key,value in update_keywords.items():
        header[key] = value

    fh.flush()
    fh.close()

    return update_keywords

def update_header_from_keywords(filename, keywords):

    fh = fits.open(filename, mode='update')

    header = fh[0].header

    for key in keywords:
        header[key] = keywords[key]

    fh.flush()
    fh.close()


if __name__ == "__main__":
    basepath = '/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/'

    suffixes = ["alpha.error.fits", "alpha.fits", "image.tt0.pbcor.fits",
                "image.tt1.fits", "image.tt1.pbcor.fits", "mask.fits",
                "model.tt0.fits", "pb.tt0.fits", "psf.tt0.fits",
                "psf.tt1.fits", "psf.tt2.fits", "residual.tt0.fits", ]

    import os
    for root, dirs, files in os.walk(basepath):
        for name in files:
            if name.endswith(".image.tt0.fits"):
                fullpath = os.path.join(root, name)
                if has_history(fullpath):
                    keywords = update_header_from_history(fullpath)
                else:
                    print(f"{fullpath} has no HISTORY")

                basename = name.split(".image.tt0.fits")[0]
                for suffix in suffixes:
                    fullpath = os.path.join(root, ".".join([basename, suffix]))
                    if os.path.exists(fullpath):
                        update_header_from_keywords(fullpath, keywords)


                if 'W51-E/B3/bsens' in fullpath:
                    print(fullpath, basename, keywords)
