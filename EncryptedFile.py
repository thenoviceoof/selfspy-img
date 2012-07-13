# EncryptedFile
# File object
################################################################################

import hashlib
from Crypto.Cipher import Blowfish

iv = '95534bc5'

class BlowfishEncryptedFile(object):
    def __init__(self, file_thing, mode='r', encryption_key=None, ):
        '''
        Open an encrypted file
        '''
        if isinstance(file_thing, basestring):
            self.file = open(file_thing, mode)
            self.name = file_thing
        elif isinstance(file_thing, file):
            self.file = file_thing
        else:
            raise TypeError
        self.blocksize = 8
        self.cipher = Blowfish.new(encryption_key, Blowfish.MODE_CBC, iv)
        self.mode = mode
        self.cache = ''
        self.closed = False
    def _read_block(self):
        if not self.cache:
            self.cache = self.cipher.decrypt(self.file.read(self.blocksize))
    def _write_block(self):
        self.file.write(self.cipher.encrypt(self.cache[:self.blocksize]))
        self.cache = self.cache[self.blocksize:]
    def read(self, size=None):
        tmp = ""
        if size is None:
            self._read_block()
            while self.cache:
                tmp += self.cache
                self.cache = ''
                self._read_block()
        else:
            while size:
                if self.cache and len(self.cache) > size:
                    tmp += self.cache
                    self.cache = ''
                    size -= len(self.cache)
                    self._read_block()
                else:
                    tmp += self.cache[:size]
                    size = 0
        return tmp
    def readline(size=None):
        pass
    def readlines(sizehint=None):
        pass
    def write(self, str):
        self.cache = str
        while len(self.cache) > self.blocksize:
            self._write_block()
    def writelines():
        pass
    def seek(offset, whence=None):
        pass
    def tell():
        pass
    def close(self):
        if self.mode == 'w':
            self.cache += '\0' * (self.blocksize - len(self.cache))
            self._write_block()
        self.file.close()

    def flush():
        self.file.flush()
    def isatty():
        return False

if __name__=='__main__':
    '''
    Documentation and self-testing
    '''
    import time
    m = hashlib.sha256()
    m.update(time.ctime())
    msg = m.hexdigest() + 'aoeuhtns'
    print(msg)

    b = BlowfishEncryptedFile('mu', 'w', 'aoeu')
    b.write(msg)
    b.close()

    b = BlowfishEncryptedFile('mu', 'r', 'aoeu')
    print(b.read())
    b.close()
