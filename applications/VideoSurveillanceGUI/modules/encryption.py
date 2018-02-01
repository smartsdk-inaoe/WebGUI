# -*- coding: utf-8 -*-

"""@package encryption
  Auxiliary module to encrypt/decrypt the password of the user
  
  @author Marlon Garcia

  Project: SmartSDK-Security

  Institution: INAOE
"""

from gluon.http import HTTP
import gluon.contrib.aes as AES
import base64
import os
 
def crypt(action, data, iv_random=True):
    try:
        # key, it has to be 128, 192, o 256 bits, check configuration
        key = 'This is a key256 XXXX XX X XXXXX'
 
        # Initialization vector. It has the first 16 bytes in the message.
        # it is used to have the same message encrypted but with different result
        # CBCMode de AES
        if iv_random:
            iv = os.urandom(16 * 1024)[0:16]
        else:
            # This case should be for the emails
            iv = ' ' * 16
 
        # The information of the message have to be multiple of 16 (AES block size), for this reason PADDING.
        # PADDING Guarantees that the message is multiple of the block
        padding = ' '
        pad = lambda s:  s + (16 - len(s) % 16) * padding
 
        if action == 'encrypt':
            return base64.b64encode(iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(data)))
        elif action == 'decrypt':
            return AES.new(key, AES.MODE_CBC, data[:16]).decrypt(base64.b64decode(data).rstrip(padding))[16:].rstrip(padding)
    except Exception as e:
        HTTP(str(e))