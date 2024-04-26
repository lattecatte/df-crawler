class Item:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.location_name = []
        self.location_link = []
        self.price = [] # array because multiple sources of the item
        self.required_item_name = []
        self.required_item_link = []
        self.sellback = []
        self.dc = []

    def append_attr(self, attr, value):
        self.__dict__[attr].append(value)

    def add_name_description(self, name, description):
        self.name = name
        self.description = description

item_list = []
items = {}