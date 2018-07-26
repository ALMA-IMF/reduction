from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc8b2b0_X6bea', 'uid___A002_Xca3f23_X2452'], session=['session_1', 'session_2'], ocorr_mode='ca')
finally:
    h_save()
