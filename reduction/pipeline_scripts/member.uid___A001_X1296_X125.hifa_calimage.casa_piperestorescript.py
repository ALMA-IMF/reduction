__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xcaca82_X3786', 'uid___A002_Xcaca82_X41c6'], session=['session_1', 'session_2'], ocorr_mode='ca')
finally:
    h_save()
