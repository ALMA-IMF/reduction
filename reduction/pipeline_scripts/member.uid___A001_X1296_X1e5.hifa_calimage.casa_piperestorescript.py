from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc86fe5_X7a9e', 'uid___A002_Xc89480_X57ef'], session=['session_2', 'session_3'], ocorr_mode='ca')
finally:
    h_save()
