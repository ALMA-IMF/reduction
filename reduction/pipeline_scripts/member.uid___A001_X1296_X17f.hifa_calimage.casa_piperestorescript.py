from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc5c71f_X34ad', 'uid___A002_Xc63024_X2cf5'], session=['session_1', 'session_2'], ocorr_mode='ca')
finally:
    h_save()
