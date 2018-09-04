import types

modules = ["data"]

for modulename in modules:
    module = __import__(modulename, globals(), locals(), [], 1)
    for v in dir(module):
        if v[0] == '_' or isinstance(getattr(module,v), types.ModuleType):
            continue
        globals()[v] = getattr(module, v)
    del module

del modules, modulename, types
