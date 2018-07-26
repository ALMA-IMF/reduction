__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xc74b5b_X536b', 'uid___A002_Xc7e4e4_X397c', 'uid___A002_Xc805c1_X379e', 'uid___A002_Xc805c1_X4055', 'uid___A002_Xc81f73_X4f1', 'uid___A002_Xc82bb8_X3948', 'uid___A002_Xc8592e_X7354'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_5', 'session_6', 'session_8'], ocorr_mode='ca')
finally:
    h_save()
