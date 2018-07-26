from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xcb402e_X2a09', 'uid___A002_Xcb402e_X36f0', 'uid___A002_Xcb4a8e_X49e8', 'uid___A002_Xcbdb2a_X613b'], session=['session_1', 'session_1', 'session_2', 'session_3'], ocorr_mode='ao')
finally:
    h_save()
