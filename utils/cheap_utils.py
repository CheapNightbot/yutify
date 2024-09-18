def is_kinda_same(a: str, b: str) -> bool:
    """Helper function to losely compare two strings.

    Args:
        a (str): Any valid string
        b (str): Any valid string

    Returns:
        bool: Return `True` or `False` based on if two strings are (kinda) same.
    """
    if (
        a.lower() != b.lower()
        and a.lower() not in b.lower()
        and b.lower() not in a.lower()
    ):
        return False

    else:
        return True


def sep_artists(artists: str, separater: str = None) -> list:
    """Separate artist names of a song or album.

    Args:
        artists (str): Artists (e.g. artistA & artistB, artistA ft. artistB, etc.)
        separater (str, optional): The separater or artist names used (if you already know). Defaults to None.

    Returns:
        list: List of artists.
    """
    separaters = [
        (";", ","),
        ("/", ","),
        ("ft", ","),
        ("ft.", ","),
        ("feat", ","),
        ("feat.", ","),
        ("with", ","),
        ("&", ","),
        ("and", ","),
    ]

    if not separater:
        for old, new in separaters:
            artists = artists.replace(old, new)

        temp = artists.split(sep=",")
        artists = []
        for i in temp:
            artists.append(i.strip())

        return artists

    artists = artists.replace(separater, ",")
    temp = artists.split(sep=",")
    artists = []
    for i in temp:
        artists.append(i.strip())

    return artists
