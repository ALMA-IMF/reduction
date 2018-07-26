from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc74b5b_X4c87', 'uid___A002_Xc7e4e4_X445f'], session=['session_1', 'session_4'], ocorr_mode='ca')
finally:
    h_save()
