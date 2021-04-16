class TACLError(Exception):

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class MalformedCatalogueError(TACLError):

    pass


class MalformedDataStoreError(TACLError):

    pass


class MalformedQueryError(TACLError):

    pass


class MalformedResultsError(TACLError):

    pass


class MalformedNormaliserMappingError(TACLError):

    def __init__(self, form, msg):
        self._form = form
        self._msg = msg

    def __str__(self):
        return self._msg.format(self._form)


class MalformedSplitConfigurationError(TACLError):

    pass
