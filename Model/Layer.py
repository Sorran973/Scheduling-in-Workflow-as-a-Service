class Layer:
    def __init__(self, node_id=None, CF_of_layer=None, option=None, previous_layer=None):
        self.node_id = node_id
        self.CF_of_layer = CF_of_layer
        self.option = option
        self.previous_layer = previous_layer