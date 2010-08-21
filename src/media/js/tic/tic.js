dojo.require("dojox.lang.aspect");
dojo.addOnLoad(function(){
    // hijack the dojo.toJson method so that we can serialize dates
    var dateSerializer = {
        around: function(obj){
            return dateSerializerHandler(obj)
        }
    }

    // hijack the dojo.fromJson method so that we can serialize dates
    var dateDeSerializer = {
        around: function(json){
            return dateDeSerializerHandler(json)
        }
    }
    var dateDeSerializerHandler = function(json){
        json = json.replace(/\"(new Date\(\d+\))\"/, '$1');
        return eval("(" + json + ")"); // Object
    }

    var dateSerializerHandler = function(it){
        if(it === undefined){
            return "undefined";
        }
        var objtype = typeof it;
        if(objtype == "number" || objtype == "boolean"){
            return it + "";
        }
        if(it === null){
            return "null";
        }
        if(dojo.isString(it)){
            return dojo._escapeString(it);
        }

        if(it instanceof Date){
            return it.getTime() + "";
        }
        // recurse
        var recurse = arguments.callee;
        // short-circuit for objects that support "json" serialization
        // if they return "self" then just pass-through...
        var newObj;
        var nextIndent = "";
        var tf = it.__json__||it.json;
        if(dojo.isFunction(tf)){
            newObj = tf.call(it);
            if(it !== newObj){
                return recurse(newObj);
            }
        }
        if(it.nodeType && it.cloneNode){ // isNode
            // we can't seriailize DOM nodes as regular objects because they have cycles
            // DOM nodes could be serialized with something like outerHTML, but
            // that can be provided by users in the form of .json or .__json__ function.
            throw new Error("Can't serialize DOM nodes");
        }

        var sep = "";
        var newLine = "";

        // array
        if(dojo.isArray(it)){
            var res = dojo.map(it, function(obj){
                var val = recurse(obj);
                if(typeof val != "string"){
                    val = "undefined";
                }
                return newLine + val;
            });
            return "[" + res.join("," + sep) + newLine + "]";
        }
        if(objtype == "function"){
            return null; // null
        }
        // generic object code path
        var output = [], key;
        for(key in it){
            var keyStr, val;
            if(typeof key == "number"){
                keyStr = '"' + key + '"';
            }else if(typeof key == "string"){
                keyStr = dojo._escapeString(key);
            }else{
                // skip non-string or number keys
                continue;
            }
            val = recurse(it[key]);
            if(typeof val != "string"){
                // skip non-serializable values
                continue;
            }
            // FIXME: use += on Moz!!
            //	 MOW NOTE: using += is a pain because you have to account for the dangling comma...
            output.push(newLine  + keyStr + ":" + sep + val);
        }
        return "{" + output.join("," + sep) + newLine + "}";
    };

    var aop = dojox.lang.aspect
    aop.advise(dojo, "toJson", dateSerializer);
    aop.advise(dojo, "fromJson", dateDeSerializer);
});

