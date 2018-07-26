from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xcc3ae3_X11aa8', 'uid___A002_Xcccc19_Xa854', 'uid___A002_Xcd1950_X2f15', 'uid___A002_Xcd3dcc_X1a3b', 'uid___A002_Xcd4e14_X1b27'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_6'], ocorr_mode='ao')
finally:
    h_save()
