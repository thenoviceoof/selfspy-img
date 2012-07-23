# EncryptedFile
# File object
################################################################################

import hashlib
from Crypto.Cipher import Blowfish, AES
from os import urandom
import math

class EncryptedFile(object):
    BLOWFISH = 4
    AES128 = 7
    AES196 = 8
    AES256 = 9

    S2K_SIMPLE = 0
    S2K_SALTED = 1
    S2K_ITERATED = 3

    HASH_MD5 = 1
    HASH_SHA1 = 2
    HASH_SHA256 = 8
    HASH_SHA384 = 9
    HASH_SHA512 = 10

    def __init__(self, file_obj, encryption_key, mode='wb', iv=None,
                 block_size=16, buffer_size=1024, timestamp=None):
        '''
        Open a pipe to an encrypted file

        file_obj: a string or file-like object
            a string should be a path
            file object: write through to the file

        mode: usual file modes
        encryption_key: passphrase

        block_size: used by the cipher
        buffer_size: how much data should be slurped up before encrypting
        timestamp <int>: timestamp, if any, to be attached to the literal data
            if not given, just writes zeroes
        '''
        if not int(buffer_size/block_size)*block_size == buffer_size:
            raise ValueError('buffer_size is not a multiple of the block_size')
        self.block_size = block_size
        # check buffer_size: can set later
        if not buffer_size > 512:
            raise ValueError('First block_size must be larger than 512b')
        self.buffer_size = buffer_size

        self.mode = mode
        if len(self.mode)>1:
            self.bin_mode = self.mode[1] == 'b'
        self._raw_buffer = ''
        self._lit_buffer = ''
        self._enc_buffer = ''
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

        if mode[0] == 'w':
            if not iv:
                self.iv = urandom(self.block_size)
            # write the symmetric encryption session packet
            self.file.write(chr((1 << 7) | (1 << 6) | 3))
            self.file.write(chr(4)) # header length
            self.file.write(chr(4)) # version
            self.file.write(chr(self.AES256)) # sym algo

            self.file.write(chr(self.S2K_SIMPLE)) # S2K
            self.file.write(chr(self.HASH_SHA256)) # S2K hash algo
            # write the encrypted data packet header
            self.file.write(chr((1 << 7) | (1 << 6) | 9))
        else:
            raise ValueError('Only \'wb\' mode supported')

        hsh = hashlib.sha256()
        hsh.update(encryption_key)
        self.key = hsh.digest()
        self.cipher = AES.new(self.key, AES.MODE_OPENPGP,
                              self.iv, block_size = block_size)

        # add the literal block id byte to the unencrypted buffer
        self._lit_buffer += chr((1 << 7) | (1 << 6) | 11)
        # set mode
        self._raw_buffer += 'b' if self.bin_mode else 't'
        # write out file name
        self._raw_buffer += chr(len(self.name))
        self._raw_buffer += self.name
        # write out 4-octet date
        if timestamp:
            self._raw_buffer += chr(timestamp >> 24 & 0xff)
            self._raw_buffer += chr(timestamp >> 16 & 0xff)
            self._raw_buffer += chr(timestamp >> 8  & 0xff)
            self._raw_buffer += chr(timestamp & 0xff)
        else:
            self._raw_buffer += '\0' * 4

    def _semi_length(self):
        '''
        Produce the byte encoding an intermediate block of data
        '''
        # make sure the buffer size fits the semi-packet length constraints
        # keep this here, self.buffer_size is user-available
        power = int(math.log(1024, 2))
        assert self.buffer_size == 2**power
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

    def _write_enc_buffer(self, final=False):
        '''
        Given things in the encrypted buffer, write them
        '''
        while len(self._enc_buffer) >= self.buffer_size:
            self.file.write(self._semi_length())
            # write the encrypted data in blocks
            self.file.write(self._enc_buffer[:self.buffer_size])
            self._enc_buffer = self._enc_buffer[self.buffer_size:]

        if final:
            self.file.write(self._final_length(len(self._enc_buffer)))
            self.file.write(self._enc_buffer)
    def _encrypt_buffer(self, final=False):
        '''
        Given literal packet data, encrypt it
        '''
        cnt = int(math.floor(len(self._lit_buffer)/self.block_size))
        bs = cnt * self.block_size
        # encrypt all data that fits cleanly in the block size
        self._enc_buffer += self.cipher.encrypt(self._lit_buffer[:bs])
        self._lit_buffer = self._lit_buffer[bs:]

        if final:
            self._enc_buffer += self.cipher.encrypt(self._lit_buffer)

        self._write_enc_buffer(final=final)
    def _write_buffer(self, final=False):
        '''
        Given things in the raw buffer, attach metadata and put them
        in the literal buffer
        '''
        # add the literal data packet metadata
        while len(self._raw_buffer) >= self.buffer_size:
            self._lit_buffer += self._semi_length()
            # write/encrypt the literal data in blocks
            self._lit_buffer += self._raw_buffer[:self.buffer_size]
            self._raw_buffer = self._raw_buffer[self.buffer_size :]
            

        if final:
            final_len = self._final_length(len(self._raw_buffer))
            self._lit_buffer += final_len
            self._lit_buffer += self._raw_buffer

        self._encrypt_buffer(final=final)

    def write(self, data):
        self._raw_buffer += data
        self._write_buffer()
    def writelines(self, lines):
        if self.bin_mode:
            raise ValueError('Textual method used with binary data')
        for line in lines:
            self._raw_buffer += line
            self._raw_buffer += '\r\n' # use CR/LF
        self._write_buffer()

    def seek(offset, whence=None):
        pass
    def tell():
        pass

    def close(self):
        self._write_buffer(final=True)
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
    msg = 'aa' * 1000
    print(msg)

    b = EncryptedFile('mu.gpg', encryption_key='w')
    b.write(msg)
    b.close()
