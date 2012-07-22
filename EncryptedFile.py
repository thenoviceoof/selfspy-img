# EncryptedFile
# File object
################################################################################

import hashlib
from Crypto.Cipher import Blowfish
from os import urandom

class BlowfishEncryptedFile(object):
    def __init__(self, file_obj, mode='r', encryption_key=None, iv=None,
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
        timestamp: timestamp, if any, to be attached to the literal data
            if not given, just writes zeroes
        '''
        # check that we can write our cache all in one go
        if not (cache_size / block_size) * block_size == cache_size:
            raise ValueError('cache_size must be a multiple of the block_size')
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
            self.file = open(file_obj, mode)
            self.name = file_obj
        elif isinstance(file_obj, file):
            self.file = file_obj
            self.name = file_obj.name
        else:
            raise TypeError

        if mode == 'w':
            # if iv:
            #     self.iv = urandom(self.blocksize)
            self.iv = chr(0) * 8
            # write the symmetric encryption session packet
            pass
            # write the encrypted data packet header
            self.file.write(chr(1 << 7 | 9))
        else:
            raise ValueError('Only \'w\' mode supported')

        self.cipher = Blowfish.new(encryption_key, Blowfish.MODE_CBC, self.iv,
                                   block_size = block_size)

        # add the literal block id byte to the unencrypted cache
        self.lit_cache += chr(1 << 7 | 11)
        # mode ['b', 't']
        self.lit_cache += 'b'
        # write out file_name
        self.lit_cache += chr(len(file_name))
        self.lit_cache += file_name
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

    # def _read_block(self):
    #     if not self.cache:
    #         self.cache = self.cipher.decrypt(self.file.read(self.blocksize))

    def _write_enc(self, data):
        '''
        Encrypt data and write it to a file
        '''
        enc = self.cipher.encrypt(data)
        self.file.write(enc)
    def _write_enc_cache(self, final=False):
        '''
        Given things in the to-be-encrypted cache, write them
        '''
        while len(self.enc_cache) >= self.cache_size:
            # write semi-length byte
            self.file.write(self._semi_length())
            # write the actual data
            for i in range(self.cache_size):
                start = self.blocksize * i
                end = self.blocksize * (i + 1)
                self._write_enc(self.cache[start:end])
            self.enc_cache = self.enc_cache[self.cache_size:]
        if final:
            # write the rest of the length
            self.file.write(self._final_length())
            ## do we need to pad?
            # write the rest of the data
            write_
    def _write_cache(self, final=False):
        # write out the rest of the block
        if final:
            length = len(self.lit_cache)

            self.enc_cache += self.lit_cache
        # check if we're good to write
        
        self.file.write(self.cipher.encrypt(self.cache[:self.blocksize]))
        self.cache = self.cache[self.blocksize:]
    # def read(self, size=None):
    #     tmp = ""
    #     if size is None:
    #         self._read_block()
    #         while self.cache:
    #             tmp += self.cache
    #             self.cache = ''
    #             self._read_block()
    #     else:
    #         while size:
    #             if self.cache and len(self.cache) > size:
    #                 tmp += self.cache
    #                 self.cache = ''
    #                 size -= len(self.cache)
    #                 self._read_block()
    #             else:
    #                 tmp += self.cache[:size]
    #                 size = 0
    #     return tmp
    # def readline(size=None):
    #     pass
    # def readlines(sizehint=None):
    #     pass
    def write(self, str):
        self.lit_len += len(str)
        self.cache += str
        self._write_cache()
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
        # go back and write the actual block lengths
        self.file.seek(-self.len-, 1)
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
