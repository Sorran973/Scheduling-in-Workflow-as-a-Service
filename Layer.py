class Layer:
    def __init__(self, node_id=[], CF_current_layer=[], options=[], previous_layers=[]):
        self.node_id = node_id
        self.CF_layer = CF_current_layer
        self.options = options
        self.previous_layers = previous_layers