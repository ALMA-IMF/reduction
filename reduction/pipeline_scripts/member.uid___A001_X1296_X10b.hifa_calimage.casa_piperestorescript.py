from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc6d2f9_X54b3', 'uid___A002_Xc6e968_X4e3b', 'uid___A002_Xc7111c_X4b2', 'uid___A002_Xc790bf_X5527', 'uid___A002_Xc7a409_X3cca'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_5'], ocorr_mode='ca')
finally:
    h_save()
