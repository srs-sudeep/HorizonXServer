# Helper to get enum key from value
def get_enum_key_from_value(enum_cls, value):
    for k in enum_cls.__members__:
        if enum_cls.__members__[k].value == value:
            return k
    return None