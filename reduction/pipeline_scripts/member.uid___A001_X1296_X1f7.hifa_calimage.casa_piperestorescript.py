from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xca6c94_X4f8b'], session=['session_1'], ocorr_mode='ca')
finally:
    h_save()
