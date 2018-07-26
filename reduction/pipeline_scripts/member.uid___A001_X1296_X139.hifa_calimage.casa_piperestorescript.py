__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xca9e6b_Xc252'], session=['session_1'], ocorr_mode='ca')
finally:
    h_save()
