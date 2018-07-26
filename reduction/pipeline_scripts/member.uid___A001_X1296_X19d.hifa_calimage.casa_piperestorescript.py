from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc86fe5_X6ab1', 'uid___A002_Xc89480_Xe6a4', 'uid___A002_Xc8cb70_X6ded', 'uid___A002_Xc8ed16_X55c7', 'uid___A002_Xc8ed16_X612d', 'uid___A002_Xca0142_X2006', 'uid___A002_Xca0a7b_X3cab', 'uid___A002_Xca0a7b_X4806', 'uid___A002_Xca0a7b_X5124'], session=['session_1', 'session_2', 'session_4', 'session_5', 'session_7', 'session_8', 'session_9', 'session_9', 'session_10'], ocorr_mode='ca')
finally:
    h_save()
