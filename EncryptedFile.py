# EncryptedFile
# File object
################################################################################

import hashlib
from Crypto.Cipher import Blowfish
from os import urandom

class BlowfishEncryptedFile(object):
    def __init__(self, file_obj, encryption_key, mode='w', iv=None,
                 block_size=8, cache_size=1024, timestamp=None):
        '''
        Open a pipe to an encrypted file

        file_obj: a string or file-like object
            a string should be a path
            file object: write through to the file

        mode: usual file modes
        encryption_key: passphrase

        block_size: used by the cipher
        cache_size: how much data should be slurped up before encrypting
        timestamp <int>: timestamp, if any, to be attached to the literal data
            if not given, just writes zeroes
        '''
        self.block_size = block_size
        # check cache_size: can set later
        if not  cache_size > 512:
            raise ValueError('First block_size must be larger than 512b')
        self.cache_size = cache_size

        self.mode = mode
        self.lit_cache = ''
        self.enc_cache = ''
        self.closed = False

        if isinstance(file_obj, basestring):
            if len(file_obj) > 0xff:
                raise ValueError('File name is too long')
            self.file = open(file_obj, mode)
            self.name = file_obj
        elif isinstance(file_obj, file):
            self.file = file_obj
            self.name = file_obj.name[:0xff]
        else:
            raise TypeError

        ### !!! binary flag does something: text -> CR/LF format
        if mode == 'wb':
            # if iv:
            #     self.iv = urandom(self.blocksize)
            self.iv = chr(0) * 8
            # write the symmetric encryption session packet
            pass
            # write the encrypted data packet header
            self.file.write(chr(1 << 7 | 9))
        else:
            raise ValueError('Only \'wb\' mode supported')

        self.cipher = Blowfish.new(encryption_key, Blowfish.MODE_OPENPGP,
                                   self.iv, block_size = block_size)

        # add the literal block id byte to the unencrypted cache
        self.lit_cache += chr(1 << 7 | 11)
        # mode ['b', 't']
        self.lit_cache += 'b'
        # write out file name
        self.lit_cache += chr(len(self.name))
        self.lit_cache += self.name
        # write out 4-octet date
        if timestamp:
            self.lit_cache += chr(timestamp >> 24 & 0xff)
            self.lit_cache += chr(timestamp >> 16 & 0xff)
            self.lit_cache += chr(timestamp >> 8  & 0xff)
            self.lit_cache += chr(timestamp & 0xff)
        else:
            self.lit_cache += '\0'*32

    def _semi_length(self):
        '''
        Produce the byte encoding an intermediate block of data
        '''
        # make sure the cache size fits the semi-packet length constraints
        # keep this here, self.cache_size is user-available
        power = int(math.log(1024, 2))
        assert self.cache_size == 2**power)
        return chr(224 + power)
    def _final_length(self, length):
        '''
        Produce the bytes encoding the length of the final data segment
        '''
        if length <= 191:
            return chr(length)
        elif length <= 8383:
            return (chr(((length - 192) >> 8) + 192) +
                    chr((length - 192) & 0xFF))
        else:
            return (chr(0xff) +
                    chr((length >> 24) & 0xff) +
                    chr((length >> 16) & 0xff) +
                    chr((length >> 8)  & 0xff) +
                    chr(length & 0xff))

    def _write_enc_cache(self, final=False):
        '''
        Given things in the encrypted cache, write them
        '''
        i = 0
        while len(self.enc_cache) >= self.cache_size:
            self.file.write(self._semi_length())
            # write the encrypted data in blocks
            start = self.blocksize * i
            end = self.blocksize * (i + 1)
            self.file.write(self.enc_cache[start:end])
            i += 1
        self.enc_cache = self.enc_cache[self.cache_size * i:]

        if final:
            self.file.write(self._final_length())
            self.file.write(self.enc_cache)
    def _write_cache(self, final=False):
        '''
        Given things in the literal cache, encrypt and put them in the
        encrypted cache
        '''
        i = 0
        while len(self.lit_cache) >= self.cache_size:
            self.enc_cache += self.cipher.encrypt(self._semi_length())
            # write/encrypt the literal data in blocks
            start = self.blocksize * i
            end = self.blocksize * (i + 1)
            self.enc_cache += self.cipher.encrypt(self.lit_cache[start:end])
            i += 1
        self.lit_cache = self.lit_cache[self.cache_size * i:]

        if final:
            self.enc_cache += self.cipher.encrypt(self._final_length())
            self.enc_cache += self.cipher.encrypt(self.lit_cache)

    def write(self, data):
        self.lit_cache += data
        self._write_cache()
    def writelines():
        pass

    def seek(offset, whence=None):
        pass
    def tell():
        pass

    def close(self):
        self._write_cache(final=True)
        self.file.close()

    def flush():
        '''
        Merely flushes the encapsulated file object
        '''
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
