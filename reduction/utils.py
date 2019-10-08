import os

def validate_mask_path(fname, rootdir='./'):
    '''Validate the mask file path
    '''

    if os.path.exists(fname):
        return fname
    else:
        aux = os.path.join(rootdir, fname)
        if os.path.exists(aux):
            return aux
        else:
            aux = os.path.join(rootdir, 'clean_regions', fname)
            if os.path.exists(aux):
                return aux
            else:
                raise IOError("Mask {0} not found".format(fname))
