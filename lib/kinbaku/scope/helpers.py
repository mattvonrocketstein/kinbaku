""" kinbaku.scope.helpers

    helpers and component glue
"""
class PythoscopeVox:
    """ MOCK: a place for pythoscope to talk out into """
    @staticmethod
    def pythoscope_vox(*args, **kargs):
        report('   ', *args, **kargs)
    write = pythoscope_vox
from pythoscope import logger
logger.set_output(PythoscopeVox)
