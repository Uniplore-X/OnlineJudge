import random
import sys
import uuid
import hashlib


def random_unique_code():
    nonce = str(random.randint(1000000, sys.maxsize))
    u = str(uuid.uuid1())
    sha1 = sha1hex(nonce + u)
    return sha1


def sha1hex(content: str):
    sha1 = hashlib.sha1()
    sha1.update(bytes(content, 'utf-8'))
    result = sha1.hexdigest()
    return result
