from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xcf3a9c_X2efb', 'uid___A002_Xcf4672_X1a17'], session=['session_1', 'session_2'], ocorr_mode='ao')
finally:
    h_save()
