'''
Created on Nov 12, 2013

@author: pixo
'''
import os

def getBadassVersion():
    """
    This function return the version of the AssetManager Badass.
    :returns:  str -- The assetmanager used version
    
    **Example:**
    
    >>> getBadassVersion ()
    >>> '0.1.0'
    
    """

    from badass import version as VERSION
    return VERSION

def getCurrentUser():
    return os.getenv ("USER")
