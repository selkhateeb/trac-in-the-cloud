

def object_mapper(source, destination):
    """
    Maps all attributes in the source object to attributes in
    destination object.

    if attributes in the destination object do not exit they will be created.

    This comes in handy in mapping comming in 'commands' to data model objects.

    Args:
        source:
            the copy-from object

        destination:
            the copy-to object

    Returns:
        the destination object

    Tests & Examples:
        >>> class A():
        ...     def __init__(self):
        ...         self.a = "this is cool"
        ...
        >>> class B():
        ...     pass
        ...
        >>> a = A()
        >>> object_mapper(a, B()).a
        'this is cool'

    """
    arr = [x for x in dir(source) if not x.startswith("__")]
    for attr in arr:
        val = getattr(source, attr)
        setattr(destination, attr, val)

    return destination