#!/usr/bin/env python

class   Bunch( dict ):
    def __init__( self, *args, **kwargs ):
        dict.__init__( self, *args, **kwargs )
        self.__dict__ = self
    def __getstate__( self ):
        return self
    def __setstate__( self, state ):
        self.update( state )
        self.__dict__ = self

if __name__ == '__main__':
    b = Bunch(
        xyz = 1,
        k = 'ah-ha',
    )
    b.abc = 123
    print b
    print b.abc
