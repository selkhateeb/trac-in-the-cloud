"""The jsonpickle.tags module provides the custom tags
used for pickling and unpickling Python objects.

These tags are keys into the flattened dictionaries
created by the Pickler class.  The Unpickler uses
these custom key names to identify dictionaries
that need to be specially handled.
"""
import re
from tic.utils.jsonpickle.compat import set

DATE_REG_EXP = re.compile("^new Date\((?P<unix_time>\d+)\)$")

OBJECT = 'declaredClass' # customizes to match the dojo specs
TYPE = 'py/type'
REPR = 'py/repr'
REF = 'py/ref'
TUPLE = 'py/tuple'
SET = 'py/set'
SEQ = 'py/seq'
STATE = 'py/state'

# All reserved tag names
RESERVED = set([OBJECT, TYPE, REPR, REF, TUPLE, SET, SEQ, STATE])
