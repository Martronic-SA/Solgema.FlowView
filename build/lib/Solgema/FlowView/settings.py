from zope.interface import implements
from persistent.dict import PersistentDict
try:
    #For Zope 2.10.4
    from zope.annotation.interfaces import IAnnotations
except ImportError:
    #For Zope 2.9
    from zope.app.annotation.interfaces import IAnnotations

from interfaces import IFlowViewSettings

class FlowViewSettings(object):
    """
    Just uses Annotation storage to save and retrieve the data...
    """
    implements(IFlowViewSettings)
    
    defaults = {}
    
    def __init__(self, context, interfaces=[IFlowViewSettings]):

        self.context = context
        
        self._interfaces = interfaces
        if type(self._interfaces) not in (list, tuple):
            self._interfaces = [self._interfaces]
        self._interfaces = list(self._interfaces)
        if IFlowViewSettings not in self._interfaces:
            self._interfaces.append(IFlowViewSettings)
        
        annotations = IAnnotations(context)

        self._metadata = annotations.get('Solgema.FlowView', None)
        if self._metadata is None:
            self._metadata = PersistentDict()
            annotations['Solgema.FlowView'] = self._metadata
            
    def __setattr__(self, name, value):
        if name in ('context', '_metadata', '_interfaces', 'defaults'):
            self.__dict__[name] = value
        else:
            self._metadata[name] = value
            
    def __getattr__(self, name):
        default = None
        
        if self.defaults.has_key(name):
            default = self.defaults[name]
        
        for iface in self._interfaces:
            if name in iface.names():
                default = iface[name].default
                        
        return self._metadata.get(name, default)

