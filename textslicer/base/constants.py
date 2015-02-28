"""
Global text processing constants
"""

import os
import re
try:
    import cPickle as pickle
except ImportError:
    import pickle

DEBUG = False

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REGEX_FLAGS = re.IGNORECASE|re.UNICODE|re.X|re.DOTALL|re.MULTILINE
