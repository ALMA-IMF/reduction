from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc89480_X5f49', 'uid___A002_Xc89480_X67a2', 'uid___A002_Xc89480_Xfb30', 'uid___A002_Xc8b2b0_X7f0d', 'uid___A002_Xc8b2b0_X8853', 'uid___A002_Xc8d560_X7abc', 'uid___A002_Xc92012_Xe8b', 'uid___A002_Xc92fe3_X7c3b'], session=['session_2', 'session_2', 'session_3', 'session_4', 'session_5', 'session_6', 'session_7', 'session_8'], ocorr_mode='ca')
finally:
    h_save()
