from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc92fe3_Xe062', 'uid___A002_Xcaf094_X3198'], session=['session_1', 'session_2'], ocorr_mode='ca')
finally:
    h_save()
