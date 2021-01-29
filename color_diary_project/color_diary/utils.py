from hashids import Hashids


SALT = 'color_diary_project by neco8'
MIN_LENGTH = 20


def get_hashids():
    hashids = Hashids(salt=SALT, min_length=20)
    return hashids