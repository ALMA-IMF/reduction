from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xcfd24b_Xab7', 'uid___A002_Xcfd24b_X14f8'], session=['session_1', 'session_1'], ocorr_mode='ao')
finally:
    h_save()
