class ReadOnlyMetaClass(type):
    def __setattr__(self, name, value) -> None: ...

class EnumMetaClass(ReadOnlyMetaClass):
    def __len__(self) -> int: ...
    def __getitem__(self, i): ...

class ExplicitEnumMetaClass(ReadOnlyMetaClass):
    def __contains__(self, item) -> bool: ...

class EnumConstant:
    def __init__(self, name, value) -> None: ...
    def __eq__(self, other): ...
    def __int__(self) -> int: ...
    def __hash__(self): ...

def EnumFactory(enum_name, enum_tuple): ...
def ExplicitEnumFactory(enum_name, enum_dict): ...
