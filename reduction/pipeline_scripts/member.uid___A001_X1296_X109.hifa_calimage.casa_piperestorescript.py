from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xcc626d_Xb34f'], session=['session_2'], ocorr_mode='ca')
finally:
    h_save()
