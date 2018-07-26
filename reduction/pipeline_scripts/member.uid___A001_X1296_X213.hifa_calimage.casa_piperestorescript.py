from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc96463_X6519', 'uid___A002_Xc96f17_X6e3d'], session=['session_1', 'session_2'], ocorr_mode='ca')
finally:
    h_save()
