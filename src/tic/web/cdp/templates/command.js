dojo.provide("{{class_name}}");
dojo.declare("{{class_name}}", null, {
    constructor: function(args){
        dojo.safeMixin(this, args);
    },
    {{properties}}
});

