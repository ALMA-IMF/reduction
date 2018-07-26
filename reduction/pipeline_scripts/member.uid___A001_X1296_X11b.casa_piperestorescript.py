from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc7a409_X351d', 'uid___A002_Xc7cf4e_X52fc', 'uid___A002_Xc7e4e4_X3ac2'], session=['session_1', 'session_2', 'session_3'], ocorr_mode='ca')
finally:
    h_save()
