# This line imports specific functions from the 'lattice' module within the same package.
# The '.' before 'lattice' indicates that it is a relative import, meaning the 'lattice' module
# is in the same package as this '__init__.py' file.
from .lattice import lattice
from .energy import energy
from .position_force import position_force
from .pressure_eV import pressure_eV
from .combine import combine
from .npz_to_extxyz import npz_to_extxyz
from .atom_symbol import atom_symbol



# The '__all__' list is a mechanism for defining what symbols (functions, classes, etc.) will be
# exported when 'from <package> import *' is used. It is a list of strings defining the names
# of the elements that should be imported.
# In this case, when someone uses 'from nequip_converter import *', only the functions 
# 'lattice'  will be imported into their namespace.
# This helps in controlling the public interface of the package and can prevent internal 
# components from being exposed unintentionally.
__all__ = ['lattice', 'energy', 'position_force', 'pressure_eV','combine','npz_to_extxyz', 'atom_symbol']