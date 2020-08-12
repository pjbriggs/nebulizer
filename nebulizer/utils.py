#!/usr/bin/env python
#
# utils: utility classes and functions for nebulizer

def size_to_bytes(size):
    """
    Convert human-readable size to bytes

    Arguments:
      size (str): human-readable size (e.g.
        '1KB','1.5GB')

    Returns:
      Integer: size converted to bytes
    """
    size = str(size).upper()
    units = ('K','M','G','T','P')
    for m,unit in enumerate(units):
        m_ = 1024**(m + 1)
        if size.endswith(unit):
            return int(float(size[:-1].strip())*m_)
        elif size.endswith("%sB" % unit):
            return int(float(size[:-2].strip())*m_)
    # No match to units, assume bytes
    return int(size)

def bytes_to_size(bytes_):
    """
    Convert bytes to human-readable size

    Arguments:
      bytes_ (int): number of bytes

    Returns:
      String: bytes converted to human-readable
        format (e.g. '1 KB','1.5 GB')
    """
    units = ('','KB','MB','GB','TB','PB')
    size = float(bytes_)
    i = 0
    while size >= 1024:
        size = size/1024.0
        i += 1
    if not units[i]:
        return "%d" % size
    else:
        size = "%.2f" % size
        if size.endswith('0'):
            size = size[:-1]
        if size.endswith('.'):
            size += '0'
    return "%s %s" % (size,units[i])
