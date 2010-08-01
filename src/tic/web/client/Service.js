/**
 *
 */
dojo.provide("tic.web.client.Service");
dojo.require("dojox.rpc.Service");
dojo.require("dojox.rpc.JsonRPC");

dojo.declare(
    "tic.web.client.Service",
    null,
    {
        _service: new dojox.rpc.Service({
            envelope:"JSON-RPC-2.0",
            transport:"POST",
            target:"/rpc",
            services:{
                "tic.rpc.api.CommandDispatcher.execute":{
                    parameters:[{
                        type:"string"
                    }] // this is optional
                }
            }
        }),

        execute: function(action){
            return this._service.tic.rpc.api.CommandDispatcher.execute(action);
        }
    });