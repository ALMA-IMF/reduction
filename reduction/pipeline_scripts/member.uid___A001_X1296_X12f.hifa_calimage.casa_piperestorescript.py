__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc805c1_X3c32', 'uid___A002_Xc805c1_X40b4', 'uid___A002_Xc82bb8_X3461'], session=['session_1', 'session_2', 'session_3'], ocorr_mode='ca')
finally:
    h_save()
