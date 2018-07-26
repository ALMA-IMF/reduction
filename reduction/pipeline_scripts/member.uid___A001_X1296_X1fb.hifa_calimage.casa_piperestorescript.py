from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc7a409_X39b5'], session=['session_2'], ocorr_mode='ca')
finally:
    h_save()
