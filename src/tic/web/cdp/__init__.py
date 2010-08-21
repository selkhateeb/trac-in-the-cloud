import datetime
import os
from google.appengine.ext.webapp import template
class Error(Exception):
    """
    Base error
    """
class BadValueError(Error):
    """
    Raised when property is set to an invalid value
    """
class DuplicatePropertyError(Error):
    """
    Duplication error
    """
    
class Property(object):
    """
    Base class for all command properties
    """

    def __init__(self):
        """Documentation"""
        self.value = None

    def __get__(self, instance, owner):
        """Documentation"""
        return self.value

    def __set__(self, instance, value):
        """ Docs """
        self.value = self.validate(value)

    def validate(self, value):
        """Validates if the value of the 'right' type"""
        if value is not None and not isinstance(value, self.data_type):
            raise BadValueError(
                                'Property %s must be %s instance, not a %s'
                                % ("self.name", self.data_type.__name__, type(value).__name__))
        return value

    def __property_config__(self, model_class, property_name):
        """Configure property, connecting it to its model.

        Configure the property so that it knows its property name and what class
        it belongs to.

        Args:
          model_class: Model class which Property will belong to.
          property_name: Name of property within Model instance to store property
            values in.  By default this will be the property name preceded by
            an underscore, but may change for different subclasses.
        """
        self.model_class = model_class
        self.name = property_name



    def to_js(self):
        """Documentation"""
        raise NotImplementedError

    def from_js(self, value):
        """Documentation"""
        raise NotImplementedError

    data_type = str

class PropertiedClass(type):
    """Meta-class for initializing Model classes properties.

  Used for initializing Properties defined in the context of a model.
  By using a meta-class much of the configuration of a Property
  descriptor becomes implicit.  By using this meta-class, descriptors
  that are of class Model are notified about which class they
  belong to and what attribute they are associated with and can
  do appropriate initialization via __property_config__.

  Duplicate properties are not permitted.
  """

    def __init__(cls, name, bases, dct):
        """Initializes a class that might have property definitions.

    This method is called when a class is created with the PropertiedClass
    meta-class.

    Loads all properties for this model and its base classes in to a dictionary
    for easy reflection via the 'properties' method.

    Configures each property defined in the new class.

    Duplicate properties, either defined in the new class or defined separately
    in two base classes are not permitted.

    Properties may not assigned to names which are in the list of
    _RESERVED_WORDS.  It is still possible to store a property using a reserved
    word in the datastore by using the 'name' keyword argument to the Property
    constructor.

    Args:
      cls: Class being initialized.
      name: Name of new class.
      bases: Base classes of new class.
      dct: Dictionary of new definitions for class.

    Raises:
      DuplicatePropertyError when a property is duplicated either in the new
        class or separately in two base classes.
      ReservedWordError when a property is given a name that is in the list of
        reserved words, attributes of Model and names of the form '__.*__'.
    """
        super(PropertiedClass, cls).__init__(name, bases, dct)

        _initialize_properties(cls, name, bases, dct)



def _initialize_properties(model_class, name, bases, dct):
    """Initialize Property attributes for Model-class.

  Args:
    model_class: Model class to initialize properties for.
  """
    model_class._properties = {}
    property_source = {}

    def get_attr_source(name, cls):
        for src_cls  in cls.mro():
            if name in src_cls.__dict__:
                return src_cls

    defined = set()
    for base in bases:
        if hasattr(base, '_properties'):
            property_keys = set(base._properties.keys())
            duplicate_property_keys = defined & property_keys
            for dupe_prop_name in duplicate_property_keys:
                old_source = property_source[dupe_prop_name] = get_attr_source(
                                                                               dupe_prop_name, property_source[dupe_prop_name])
                new_source = get_attr_source(dupe_prop_name, base)
                if old_source != new_source:
                    raise DuplicatePropertyError(
                                                 'Duplicate property, %s, is inherited from both %s and %s.' %
                                                 (dupe_prop_name, old_source.__name__, new_source.__name__))
            property_keys -= duplicate_property_keys
            if property_keys:
                defined |= property_keys
                property_source.update(dict.fromkeys(property_keys, base))
                model_class._properties.update(base._properties)

    for attr_name in dct.keys():
        attr = dct[attr_name]
        if isinstance(attr, Property):
            #check_reserved_word(attr_name)
            if attr_name in defined:
                raise DuplicatePropertyError('Duplicate property: %s' % attr_name)
            defined.add(attr_name)
            model_class._properties[attr_name] = attr
            attr.__property_config__(model_class, attr_name)


class Command(object):
    """Command is the superclass of all commands.

  The programming model is to declare Python subclasses of the Model class,
  declaring datastore properties as class members of that class. So if you want
  to publish a story with title, body, and created date, you would do it like
  this:

    class LoginCommand(Command):
      title = StringProperty()
      created = db.DateTimeProperty()
  """

    __metaclass__ = PropertiedClass

    @classmethod
    def properties(cls):
        """Returns a dictionary of all the properties defined for this model."""
        return dict(cls._properties)

    def to_js(self):
        """Generates dojo class"""
        properties = ""

        length = len(self.properties().values())
        for index, prop in enumerate(self.properties().values()):
            properties += '%s:%s' % (prop.name, prop.to_js())
            if index != length - 1:
                properties += ","

        vars = {'properties': properties, 'class_name': "%s.%s" % (self.__class__.__module__, self.__class__.__name__)}
        path = os.path.join(os.path.dirname(__file__), 'templates/command.js')
        return template.render(path, vars)

    def from_js(self, json):
        """Documentation"""
        if isinstance(json, dict):
            json_dict = json
        else:
            from tic.utils.simplejson import loads
            json_dict = loads(json)

        for key, prop in self.properties().items():
            value = json_dict[key]
            prop.from_js(value)

    def to_json(self):
        """Documentation"""
        properties = ""
        length = len(self.properties().values())
        for index, prop in enumerate(self.properties().values()):
            properties += '%s:%s' % (prop.name, prop.to_js())
            if index != length - 1:
                properties += ","

        return "{%s}" % properties

    
Result = Command


class StringProperty(Property):

    data_type = basestring
    
    def to_js(self):
        """Documentation"""
        from tic.utils.simplejson.encoder import encode_basestring
        if self.value is None:
            self.value = ""
        return encode_basestring(self.value)

    def from_js(self, value):
        """Documentation"""
        self.value = "" if value is None else value

class DateTimeProperty(Property):

    data_type = datetime.datetime

    def to_js(self):
        """Documentation"""
        return "null" if self.value is None else "new Date(%i)" % self._get_unix_epoch()

    def from_js(self, value):
        """Documentation"""
        v = None if value is None else datetime.datetime.fromtimestamp(value/1000)
        self.value = self.validate(v)

    def _get_unix_epoch(self):
        """
        returns the unix epoch in milliseconds
        """
        from time import mktime
        return int((mktime(self.value.timetuple()) + 1e-6 * self.value.microsecond) * 1000)
