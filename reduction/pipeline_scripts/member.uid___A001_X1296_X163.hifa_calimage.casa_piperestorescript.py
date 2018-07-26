from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc7111c_X8ce3', 'uid___A002_Xc7cf4e_X4338', 'uid___A002_Xc7cf4e_X8c0e', 'uid___A002_Xc805c1_X2d79'], session=['session_1', 'session_2', 'session_3', 'session_4'], ocorr_mode='ca')
finally:
    h_save()
