from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc7111c_X4e24', 'uid___A002_Xc72427_X4bae', 'uid___A002_Xc7a409_X4160', 'uid___A002_Xc7e4e4_X3f43', 'uid___A002_Xc845c0_X3850'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_6'], ocorr_mode='ca')
finally:
    h_save()
