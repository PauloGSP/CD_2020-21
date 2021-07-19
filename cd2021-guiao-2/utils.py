def dht_hash(text, seed=0, maximum=2**10):
    """ FNV-1a Hash Function. """
    fnv_prime = 16777619
    offset_basis = 2166136261
    h = offset_basis + seed
    for char in text:
        h = h ^ ord(char)
        h = h * fnv_prime
    return h % maximum


def contains(begin, end, node):
    """Check node is contained between begin and end in a ring."""
    if (node > begin and node <= end):
        return True
    elif (begin > end and (node > begin or node <= end)):
        return True
    else:
        return False
