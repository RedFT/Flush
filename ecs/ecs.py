class Component(object):
    def __init__(self, owner, component_type="component"):
        super(Component, self).__init__()
        self.owner = owner
        self.component_type = component_type

    def reload(self):
        pass


class Entity(object):
    def __init__(self, collidable=True):
        super(Entity, self).__init__()

        self.is_collidable = collidable
        self.components = []
        self.systems = []

    def __getitem__(self, key):
        return self.get_component(key)

    def get_component(self, component_type):
        """ Iterate through component list for a component with
            the matching String """
        ret_cmp = next((comp for comp in self.components
                        if comp.component_type == component_type),
                       None)
        if ret_cmp is None:
            print self, "has no " + component_type
        return ret_cmp

    def on_notify(self, entity, event):
        pass


class System(object):
    def __init__(self):
        super(System, self).__init__()

        self.registered_entities = []

    def register(self, obj):
        self.registered_entities.append(obj)
        obj.systems.append(self)

    def unregister(self, obj):
        self.registered_entities = [
            ent for ent in self.registered_entities
            if ent != obj]

    def global_kill(self, an_object):
        for sys in an_object.systems:
            sys.unregister(self)

    def update(self, speed_factor):
        pass
