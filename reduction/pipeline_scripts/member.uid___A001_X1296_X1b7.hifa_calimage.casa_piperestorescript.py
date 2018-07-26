from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xcb4a8e_X362f'], session=['session_1'], ocorr_mode='ca')
finally:
    h_save()
