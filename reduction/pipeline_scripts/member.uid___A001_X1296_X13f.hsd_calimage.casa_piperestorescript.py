from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xca9e6b_Xd3f4', 'uid___A002_Xcad526_X687b', 'uid___A002_Xcaf094_X1f06', 'uid___A002_Xcb339b_X40fe', 'uid___A002_Xcbb583_X539c', 'uid___A002_Xcc10e0_X1223', 'uid___A002_Xcc10e0_X5cea'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_5', 'session_6', 'session_7'], ocorr_mode='ao')
finally:
    h_save()
