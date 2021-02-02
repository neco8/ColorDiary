from hashids import Hashids


SALT = 'Color Diary Project by neco8'
MIN_LENGTH = 20


def get_hashids():
    hashids = Hashids(salt=SALT, min_length=MIN_LENGTH)
    return hashids