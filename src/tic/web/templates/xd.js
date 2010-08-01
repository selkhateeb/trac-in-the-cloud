window[(typeof (djConfig)!="undefined"&&djConfig.scopeMap&&djConfig.scopeMap[0][1])||"dojo"]._xdResourceLoaded(function(_1,_2,_3){
    return {
        depends:[["provide", "{{provide}}"],
            {% for require in requireList %}
            ["require","{{require}}"]{% if not forloop.last %},{% endif %}
            {%endfor%}
        ],
        defineResource:function(dojo,_5,_6){
            if(!dojo._hasResource["{{provide}}"]){
                dojo._hasResource["{{provide}}"]=true;
                }
                dojo.provide("{{provide}}");
                {% for require in requireList %}
                dojo.require("{{require}}");
                {%endfor%}
                {{declaration}}
            
        }
    };

});