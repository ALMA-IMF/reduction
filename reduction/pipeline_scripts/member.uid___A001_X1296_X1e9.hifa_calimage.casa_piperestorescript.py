from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc7fa6f_X3cc9', 'uid___A002_Xc81f73_X3a2e', 'uid___A002_Xc82bb8_X2f4d', 'uid___A002_Xc82bb8_X336f', 'uid___A002_Xc8592e_X7d0e'], session=['session_1', 'session_2', 'session_3', 'session_3', 'session_5'], ocorr_mode='ca')
finally:
    h_save()
