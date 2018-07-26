from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc7e4e4_X3096', 'uid___A002_Xc7e4e4_X352d', 'uid___A002_Xc82bb8_X2b1d'], session=['session_1', 'session_2', 'session_4'], ocorr_mode='ca')
finally:
    h_save()
