def ensureUtf(s, encoding='utf8'):
    """Converts input to unicode if necessary.
    If `s` is bytes, it will be decoded using the `encoding` parameters.
    This function is used for preprocessing /source/ and /filename/ arguments
    to the builtin function `compile`.
    """
    # In Python2, str == bytes.
    # In Python3, bytes remains unchanged, but str means unicode
    # while unicode is not defined anymore
    if type(s) == bytes:
        return s.decode(encoding, 'ignore')
    else:
        return s
