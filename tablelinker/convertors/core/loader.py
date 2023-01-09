import importlib.machinery as imm
import os


def load_dirs(dirs):
    for dir in dirs:
        load_dir(dir)


def load_dir(dir_name):
    print("load dir %s" % dir_name)
    module_dirs = os.listdir(path=dir_name)
    for module in module_dirs:
        if module in ["__init__.py", "__pycache__"]:
            continue

        module_dir = os.path.join(dir_name, module)
        module_entry = os.path.join(module_dir, "__init__.py")
        module_name = "convertors.filters." + module
        datum = imm.SourceFileLoader("" + module_name, module_entry).load_module()
        print("loaded module %s" % (datum))
