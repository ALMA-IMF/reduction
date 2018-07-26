__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc75eba_X4f72', 'uid___A002_Xc77d4f_X370b', 'uid___A002_Xc7cf4e_X57f0', 'uid___A002_Xc7e4e4_X37e3', 'uid___A002_Xc8592e_X71c2', 'uid___A002_Xc8592e_X7966'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_5', 'session_6'], ocorr_mode='ca')
finally:
    h_save()
