from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xcb339b_X50b4', 'uid___A002_Xcb4a8e_X405c', 'uid___A002_Xcb4a8e_X52b0', 'uid___A002_Xcbc47c_Xeadc', 'uid___A002_Xcbf591_X9bc1', 'uid___A002_Xcc10e0_X11fa', 'uid___A002_Xcc10e0_X1c46', 'uid___A002_Xccde5b_X387c', 'uid___A002_Xccea8d_X4bd1', 'uid___A002_Xccea8d_Xe1d1', 'uid___A002_Xcd64ec_X45ba', 'uid___A002_Xcd64ec_X5416', 'uid___A002_Xcd64ec_Xe856'], session=['session_1', 'session_3', 'session_4', 'session_5', 'session_6', 'session_7', 'session_8', 'session_9', 'session_10', 'session_11', 'session_12', 'session_12', 'session_13'], ocorr_mode='ca')
finally:
    h_save()
