from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc8ed16_X7321', 'uid___A002_Xc92fe3_Xd7bf', 'uid___A002_Xca464b_X5392', 'uid___A002_Xcb1740_X5179'], session=['session_1', 'session_2', 'session_3', 'session_4'], ocorr_mode='ca')
finally:
    h_save()
