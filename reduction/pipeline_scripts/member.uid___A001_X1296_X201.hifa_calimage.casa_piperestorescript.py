__rethrow_casa_exceptions = True
h_init()
try:
    hifa_restoredata (vis=['uid___A002_Xccb526_Xacef'], session=['session_1'], ocorr_mode='ca')
finally:
    h_save()
