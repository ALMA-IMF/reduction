from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xcb4a8e_X2bb9', 'uid___A002_Xcca365_X167f'], session=['session_1', 'session_2'], ocorr_mode='ca')
finally:
    h_save()
