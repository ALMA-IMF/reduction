__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc6d2f9_X4e1a', 'uid___A002_Xc6e968_X4486', 'uid___A002_Xc6e968_X4866'], session=['session_1', 'session_3', 'session_3'], ocorr_mode='ca')
finally:
    h_save()
