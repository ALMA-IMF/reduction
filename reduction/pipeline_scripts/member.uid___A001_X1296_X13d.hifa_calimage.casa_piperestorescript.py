__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc743d2_X185', 'uid___A002_Xc7b4ea_X4057'], session=['session_1', 'session_2'], ocorr_mode='ca')
finally:
    h_save()
