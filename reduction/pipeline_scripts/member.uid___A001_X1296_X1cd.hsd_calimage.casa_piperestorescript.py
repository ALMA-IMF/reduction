from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xcb053b_X7542', 'uid___A002_Xcb339b_X315a', 'uid___A002_Xcb339b_X4bea'], session=['session_1', 'session_2', 'session_3'], ocorr_mode='ao')
finally:
    h_save()
