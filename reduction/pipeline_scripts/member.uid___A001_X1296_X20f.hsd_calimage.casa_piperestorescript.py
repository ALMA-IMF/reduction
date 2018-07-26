from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xc9020b_X7c2e', 'uid___A002_Xc91189_X2379'], session=['session_1', 'session_2'], ocorr_mode='ao')
finally:
    h_save()
