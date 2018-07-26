from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc8ed16_X696d', 'uid___A002_Xc91189_X284b', 'uid___A002_Xc92012_X1a8e', 'uid___A002_Xc92fe3_X8038', 'uid___A002_Xc96463_X741a', 'uid___A002_Xc9957b_Xbd7', 'uid___A002_Xc9957b_X1347', 'uid___A002_Xca0142_X2950'], session=['session_3', 'session_4', 'session_5', 'session_6', 'session_7', 'session_8', 'session_8', 'session_10'], ocorr_mode='ca')
finally:
    h_save()
