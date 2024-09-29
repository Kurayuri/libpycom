from libpycom.containers.Class.TupleClass import TupleClass


class Cert(TupleClass):
    def __init__(self, CertFile=None, KeyFile=None, Password=None, **kwargs) -> None:
        self.CertFile = CertFile
        self.KeyFile = KeyFile
        self.Password = Password
