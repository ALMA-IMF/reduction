from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc845c0_X349f', 'uid___A002_Xc845c0_X3911', 'uid___A002_Xc845c0_X4842'], session=['session_2', 'session_2', 'session_3'], ocorr_mode='ca')
finally:
    h_save()
