class TACLError (Exception):

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class MalformedCatalogueError (TACLError):

    pass


class MalformedQueryError (TACLError):

    pass


class MalformedResultsError (TACLError):

    pass
