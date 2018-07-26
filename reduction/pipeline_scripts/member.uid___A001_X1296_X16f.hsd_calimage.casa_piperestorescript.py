from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xc92fe3_Xcf07', 'uid___A002_Xc92fe3_Xdfb7', 'uid___A002_Xc99ad7_X3b2f', 'uid___A002_Xc99ad7_X44c3', 'uid___A002_Xca795f_Xadfd', 'uid___A002_Xca795f_Xb668', 'uid___A002_Xcb1740_X3792'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_6', 'session_6', 'session_7'], ocorr_mode='ao')
finally:
    h_save()
