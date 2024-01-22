

import copy


class Buffer(object):
    """ Simple buffer that allows for storing objects of any type.
    """
    
    def put(self, objectToPut, identifier):
        """ Puts an object into the buffer.
        
        Parameters
        ----------
        objectToPut : any
        
        identifier : str
            Object is stored inside the buffer under string identifier.
            To retrieve the object later you need to use this identifier.
        """
        self._buffer[identifier] = objectToPut

    def take(self, identifier):
        """ Takes object out of buffer.
        
        Object does not stay in buffer after this.
        
        Parameters
        ----------
        identifier : str
        
        Raises
        ------
        LookupError
            If requested object is not in the buffer.
        """
        objectToReturn = None
        try:
            objectToReturn = copy.deepcopy(self._buffer[identifier])
            del self._buffer[identifier]
            return objectToReturn
        except KeyError:
            raise LookupError
        raise LookupError

    def __init__(self):
        self._buffer = {}