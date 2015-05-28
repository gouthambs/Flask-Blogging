

def create_slug(title):
    return "-".join([t.lower() for t in title.split()])
