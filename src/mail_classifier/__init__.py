import logging

log = logging.getLogger(__package__)
log.addHandler(logging.NullHandler())

try:
    from ._version import __version__, __longversion__
except ImportError:
    __version__ = __longversion__ = 'unknown'


