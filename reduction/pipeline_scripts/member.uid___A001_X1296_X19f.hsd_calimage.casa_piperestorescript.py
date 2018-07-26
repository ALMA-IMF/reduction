from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hsd_restoredata (vis=['uid___A002_Xcbc47c_Xdb43', 'uid___A002_Xcbc47c_Xe35b', 'uid___A002_Xcbc47c_Xec3e', 'uid___A002_Xcc3ae3_X6dbd', 'uid___A002_Xccb526_X329a', 'uid___A002_Xccb526_X9f2e', 'uid___A002_Xccb526_Xa8f2', 'uid___A002_Xccde5b_X2752', 'uid___A002_Xccde5b_X387b', 'uid___A002_Xcd07af_X2a55', 'uid___A002_Xcd07af_X466e', 'uid___A002_Xcd1950_X21e8', 'uid___A002_Xcd1950_X3bdf', 'uid___A002_Xcd2acd_X41f8', 'uid___A002_Xcd2acd_X4e6f', 'uid___A002_Xcd3dcc_X7ab', 'uid___A002_Xcd3dcc_X100e'], session=['session_1', 'session_1', 'session_1', 'session_2', 'session_5', 'session_6', 'session_6', 'session_7', 'session_8', 'session_9', 'session_10', 'session_11', 'session_12', 'session_13', 'session_13', 'session_14', 'session_14'], ocorr_mode='ao')
finally:
    h_save()
