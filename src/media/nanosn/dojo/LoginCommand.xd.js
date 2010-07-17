window[(typeof (djConfig)!="undefined"&&djConfig.scopeMap&&djConfig.scopeMap[0][1])||"dojo"]._xdResourceLoaded(function(_1,_2,_3){
    return {
        depends:[
        ["provide","nanosn.dojo.LoginCommand"]],
        
        defineResource: function(_4,_5,_6){
            if(!_4._hasResource["nanosn.dojo.LoginCommand"]){
                _4._hasResource["nanosn.dojo.LoginCommand"]=true;
            }
            _4.provide("nanosn.dojo.LoginCommand");
            _4.declare("nanosn.dojo.LoginCommand", null,{
                
                a: ["Sweet", "mm"],

                hi: function(msg){
                    alert(msg);
                }
            })
        }
    }
})
