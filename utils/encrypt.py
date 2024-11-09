import hashlib
from django.conf import settings
import random
import uuid
import datetime


def md5(value):
    obj = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    obj.update(value.encode('utf-8'))
    return obj.hexdigest()


def gen_random_oid():
    rand_number = random.randint(10000000, 99999999)
    ctime = datetime.datetime().strftime("%Y%m%d%H%M%S%f")
    trans_id = "{}{}".format(ctime, rand_number)
    return trans_id
