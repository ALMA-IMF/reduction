from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xc9020b_X653b', 'uid___A002_Xc9020b_X712a', 'uid___A002_Xc92fe3_X6213', 'uid___A002_Xca5b1c_X5da9', 'uid___A002_Xca9e6b_X2e4a', 'uid___A002_Xcb339b_X205d'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_5', 'session_6'], ocorr_mode='ao')
finally:
    h_save()
