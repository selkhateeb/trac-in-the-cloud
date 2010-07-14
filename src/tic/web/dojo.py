
import tic.utils.jsonpickle as jsonpickle

def to_dojo(object):
    """converts a python class to a dojo class"""

    class_name = object.__class__.__module__ + "." + object.__class__.__name__
    json = jsonpickle.encode(object)
    
    dojo_class = 'window[(typeof (djConfig)!="undefined"&&djConfig.scopeMap&&' \
        'djConfig.scopeMap[0][1])||"dojo"]._xdResourceLoaded(' \
        'function(_1,_2,_3){return{depends:[["provide","' \
        + class_name + '"]],defineResource: function(_4,_5,_6){if(!_4._hasResource["' \
        '"]){_4._hasResource["' + class_name + '"]=true;}_4.provide("' \
        + class_name + '");_4.declare("' + class_name + '", null,' + json \
        + ')}}})'

    return dojo_class

