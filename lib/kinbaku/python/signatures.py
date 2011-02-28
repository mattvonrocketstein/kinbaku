""" kinbaku.python.signatures
"""
import pep362

from pep362 import Signature as JohnHancock

class Signature(JohnHancock):
    def __len__(self):
        return len(self._parameters)

    @property
    def has_default_values(self):
        return any([hasattr(p,'default_value') for p in self._parameters.values()])

    @property
    def default_values(self):
        items = [[k,v] for k,v in self._parameters.items() if hasattr(v,'default_value')]
        return dict([[k, v.default_value] for k,v in items])

pep362.Signature = Signature # TODO: find a way around this monkey patch
