__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc6a3db_X494f', 'uid___A002_Xc6fa08_X33b7'], session=['session_1', 'session_2'], ocorr_mode='ca')
finally:
    h_save()
