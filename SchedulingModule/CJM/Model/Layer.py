class Layer:
    def __init__(self, node=None, CF_of_layer=None, layer_options=None, previous_layers=None):
        self.node = node
        self.CF_of_layer = CF_of_layer
        self.layer_options = layer_options
        self.previous_layers = previous_layers