"""Simplex and SimplexView Classes."""

try:
    from collections.abc import Hashable, Iterable
except ImportError:
    from collections import Iterable, Hashable

from itertools import combinations

import numpy as np

__all__ = ["Simplex"]


class Simplex:
    """A class representing a simplex in a simplicial complex.

    This class represents a simplex in a simplicial complex, which is a set of nodes with a specific dimension.
    The simplex is immutable, and the nodes in the simplex must be hashable and unique.

    :param elements: The nodes in the simplex.
    :type elements: any iterable of hashables
    :param name: A name for the simplex, default is None.
    :type name: str, optional
    :param construct_tree: If True, construct the entire simplicial tree for the simplex. Default is True.
    :type construct_tree: bool, optional
    :param attr: Additional attributes to be associated with the simplex.
    :type attr: keyword arguments, optional

    :Example:
        >>> # Create a 0-dimensional simplex (point)
        >>> s = Simplex((1,))
        >>> # Create a 1-dimensional simplex (line segment)
        >>> s = Simplex((1, 2))
        >>> # Create a 2-dimensional simplex ( triangle )
        >>> simplex1 = Simplex ( (1,2,3) )
        >>> simplex2 = Simplex ( ("a","b","c") )
        >>> # Create a 3-dimensional simplex ( tetrahedron )
        >>> simplex3 = Simplex ( (1,2,4,5),weight = 1 )

    """

    def __init__(self, elements, name=None, construct_tree=True, **attr):

        if name is None:
            self.name = ""
        else:
            self.name = name
        self.construct_tree = construct_tree
        self.nodes = frozenset(elements)
        if len(self.nodes) != len(elements):
            raise ValueError("a simplex cannot contain duplicate nodes")

        if construct_tree:
            self._faces = self.construct_simplex_tree(elements)
        else:
            self._faces = frozenset()
        self.properties = dict()
        self.properties.update(attr)

    def __contains__(self, e):
        if len(self.nodes) == 0:
            return False
        if isinstance(e, Iterable):
            if len(e) != 1:
                return False
            else:
                if isinstance(e, frozenset):
                    return e <= self.nodes
                else:
                    return frozenset(e) <= self.nodes
        elif isinstance(e, Hashable):
            return frozenset({e}) in self.nodes
        else:
            return False

    @staticmethod
    def construct_simplex_tree(elements):
        faceset = set()
        numnodes = len(elements)
        for r in range(numnodes, 0, -1):
            for face in combinations(elements, r):
                faceset.add(
                    Simplex(elements=sorted(face), construct_tree=False)
                )  # any face is always ordered
        return frozenset(faceset)

    @property
    def boundary(self):
        """
        get the boundary faces of the simplex
        """
        if self.construct_tree:
            return frozenset(i for i in self._faces if len(i) == len(self) - 1)
        else:
            faces = Simplex.construct_simplex_tree(self.nodes)
            return frozenset(i for i in faces if len(i) == len(self) - 1)

    def sign(self, face):
        raise NotImplementedError

    @property
    def faces(self):
        if self.construct_tree:
            return self._faces
        else:
            return Simplex.construct_simplex_tree(self.nodes)

    def __getitem__(self, item):
        if item not in self.properties:
            raise KeyError(f"attr {item} is not an attr in the cell {self.name}")
        else:
            return self.properties[item]

    def __setitem__(self, key, item):
        self.properties[key] = item

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        return iter(self.nodes)

    def __repr__(self):
        """
        String representation of Simplex
        Returns
        -------
        str
        """
        return f"Simplex{tuple(self.nodes)}"

    def __str__(self):
        """
        String representation of a simplex
        Returns
        -------
        str
        """
        return f"Nodes set:{tuple(self.nodes)}, attrs:{self.properties}"
