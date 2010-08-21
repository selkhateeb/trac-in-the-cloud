
import tic.utils.jsonpickle as jsonpickle
#DEPRECATED
def to_dojo(object):
    """
    @Depreicated
    converts a python class to a dojo class"""

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

def render_xd_classes(js_file_path_or_content, req):
    """
    Renders the cross-domain dojo files
    """
    from google.appengine.ext.webapp import template
    import os, re
    from tic.utils.jsparser import parse
    try:
        nodes = parse(file(js_file_path_or_content).read(), js_file_path_or_content)
    except:
        nodes = parse(js_file_path_or_content)

    provide_matcher = re.compile(r'dojo.provide\("(.*)"\)')
    require_matcher = re.compile(r'dojo.require\("(.*)"\)')
    vars = {'requireList': list(), 'declaration': ""}
    for node in nodes:
        source = node.getSource()
        #dojo.provide statement?
        if provide_matcher.match(source):
            vars['provide'] = provide_matcher.findall(source)[0]

        elif require_matcher.match(source):
            vars['requireList'].append(require_matcher.findall(source)[0])
        else:
            vars['declaration'] += source + ";"

    mimetype = "application/json;charset=utf-8"
    req.send_header('Content-Type', mimetype)
    path = os.path.join(os.path.dirname(__file__), 'templates/xd.js')
    req.write(template.render(path, vars))
