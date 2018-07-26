from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc6c0d5_X3f2e', 'uid___A002_Xc6d2f9_X4380'], session=['session_1', 'session_2'], ocorr_mode='ca')
finally:
    h_save()
