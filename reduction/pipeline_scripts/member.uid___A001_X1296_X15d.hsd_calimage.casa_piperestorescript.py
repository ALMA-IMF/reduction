from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xc99ad7_Xab4a', 'uid___A002_Xcc8b19_X7112', 'uid___A002_Xcc8b19_X7d16', 'uid___A002_Xcf3a9c_X1be5', 'uid___A002_Xcf7c14_X14ca'], session=['session_1', 'session_2', 'session_2', 'session_4', 'session_5'], ocorr_mode='ao')
finally:
    h_save()
