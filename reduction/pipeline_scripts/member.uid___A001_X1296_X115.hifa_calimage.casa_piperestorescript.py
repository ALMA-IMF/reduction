from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc6141c_X2870', 'uid___A002_Xc6b674_X42f', 'uid___A002_Xc845c0_X4928', 'uid___A002_Xc96463_X6903', 'uid___A002_Xcaf094_X3cc0', 'uid___A002_Xcb1740_X5dcb', 'uid___A002_Xcb5bc7_X2eba', 'uid___A002_Xcba691_X6b8e'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_5', 'session_6', 'session_7', 'session_9'], ocorr_mode='ca')
finally:
    h_save()
