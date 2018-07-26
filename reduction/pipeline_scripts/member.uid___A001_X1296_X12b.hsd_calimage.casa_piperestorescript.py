from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xc9831a_X646c', 'uid___A002_Xc9831a_X7723', 'uid___A002_Xca0a7b_X4e0b', 'uid___A002_Xca8fbf_X707f', 'uid___A002_Xca9e6b_Xe64b', 'uid___A002_Xca9e6b_Xf5da', 'uid___A002_Xcaf094_X3588', 'uid___A002_Xcaf094_X5182', 'uid___A002_Xcb1740_X6ef4', 'uid___A002_Xcb4a8e_X549a', 'uid___A002_Xcb5bc7_X2846', 'uid___A002_Xcb8a93_Xc0cb', 'uid___A002_Xcba691_X6e74', 'uid___A002_Xcbc47c_X51de', 'uid___A002_Xcbc47c_X6495', 'uid___A002_Xcbdb2a_X13be0', 'uid___A002_Xcc10e0_X1c41', 'uid___A002_Xcc10e0_X67e5'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_5', 'session_6', 'session_7', 'session_8', 'session_9', 'session_10', 'session_11', 'session_12', 'session_13', 'session_14', 'session_14', 'session_15', 'session_16', 'session_17'], ocorr_mode='ao')
finally:
    h_save()
