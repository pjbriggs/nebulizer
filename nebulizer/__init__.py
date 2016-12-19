# Current version of the library
__version__ = '0.4.1'

def get_version():
    """Returns a string with the current version of the library (e.g., "0.2.0")

    """
    return __version__

# Setup logging
import logging
logging.basicConfig()
logger = logging.getLogger("nebulizer")
