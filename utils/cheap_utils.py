def cheap_compare(a: str, b: str) -> bool:
    """
    Loosely compare two strings.

    Args:
        a (str): Any valid string.
        b (str): Any valid string.

    Returns:
        bool: True if the strings are similar, otherwise False.
    """
    a_lower, b_lower = a.lower(), b.lower()
    return a_lower == b_lower or a_lower in b_lower or b_lower in a_lower


def sep_artists(artists: str, separator: str = None) -> list:
    """
    Separate artist names of a song or album into a list.

    Args:
        artists (str): Artists string (e.g., artistA & artistB, artistA ft. artistB).
        separator (str, optional): A specific separator to use. Defaults to None.

    Returns:
        list: List of individual artists.
    """
    separators = [";", "/", "ft", "ft.", "feat", "feat.", "with", "&", "and"]

    if not separator:
        for sep in separators:
            artists = artists.replace(sep, ",")
    else:
        artists = artists.replace(separator, ",")

    return [artist.strip() for artist in artists.split(",")]
