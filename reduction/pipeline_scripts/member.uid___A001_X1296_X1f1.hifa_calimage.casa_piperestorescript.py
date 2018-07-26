from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc5d6d1_X500c', 'uid___A002_Xc77d4f_X3cc5'], session=['session_1', 'session_2'], ocorr_mode='ca')
finally:
    h_save()
