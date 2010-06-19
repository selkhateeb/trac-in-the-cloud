#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from tic.core import Component
from tic.core import ComponentManager, ComponentMeta
from tic.core import ExtensionPoint
from tic.core import Interface
from tic.core import implements
from django.template import Template, Context

def dispatch_request(environ, start_response):
    """Main entry point for the Trac web interface.

    @param environ: the WSGI environment dict
    @param start_response: the WSGI callback for starting the response
    """

    env = Enviornment()
    
    todo_list = TodoList(env)

    todo_list.add('Make coffee',
                  'Really need to make some coffee')
    todo_list.add('Bug triage',
                  'Double-check that all known issues were addressed')

    t = Template("My name is : {{ my_name }}.")
    c = Context({"my_name": "Adrian"})
    print t.render(c)

class Enviornment(Component, ComponentManager):
    pass

class ITodoObserver(Interface):
    def todo_added(name, description):
        """Called when a to-do item is added."""

class TodoList(Component):
    observers = ExtensionPoint(ITodoObserver)

    def __init__(self):
        self.todos = {}

    def add(self, name, description):
        assert not name in self.todos, 'To-do already in list'
        self.todos[name] = description
        for observer in self.observers:
            observer.todo_added(name, description)

class TodoPrinter(Component):
    implements(ITodoObserver)

    def todo_added(self, name, description):
        print 'TODO', name
        print '     ', description
