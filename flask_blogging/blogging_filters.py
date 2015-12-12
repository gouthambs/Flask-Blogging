import jinja2


def snippet(text, length=200):
    """
    Trim the text till given length.
    :param text: Text to be trimmed
    :param length: number of characters to be kept, rest will be trimmed.
    :return: Trimmer to the length text
    """
    if text is None or not hasattr(text, '__len__'):
        return text
    t_snippet = text[:length]
    return t_snippet

jinja2.filters.FILTERS['quick_look'] = snippet
