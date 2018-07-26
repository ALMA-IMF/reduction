__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc6d2f9_X4b79'], session=['session_1'], ocorr_mode='ca')
finally:
    h_save()
