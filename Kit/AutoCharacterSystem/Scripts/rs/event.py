
""" Event interface definition.
"""


class Event(object):
    """ Interface for objects that act as events.
    
    Attributes
    ----------
    descType : str
        Type of an event, must be unique string within all event types.
    
    descUsername : str
        Username to print out in logs, etc.
    """
    
    descType = ''
    descUsername = ''

    @classmethod
    def getUsernameOrType(cls):
        """ Returns either username or type if username is not defined.
        """
        username = cls.descUsername
        if not username:
            username = cls.descType
        return username

    def __str__(self):
        return self.getUsernameOrIdentifier() + ' Event'