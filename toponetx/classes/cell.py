"""Cell and CellView classes."""

from collections import Counter, deque
from collections.abc import Collection, Iterable, Sequence
from itertools import zip_longest
from typing import Literal

from toponetx.classes.complex import Atom

__all__ = ["Cell"]


class Cell(Atom):
    """Class representing a 2D cell.

    A 2D cell is an elementary building block used to build a 2D cell complex, whether regular or non-regular.

    Parameters
    ----------
    elements : iterable of hashable objects
        An iterable that contains hashable objects representing the nodes of the cell. The order of the elements is important
        and defines the cell up to cyclic permutation.
    name : str, optional
        A string representing the name of the cell.
    regular : bool, optional
        A boolean indicating whether the cell satisfies the regularity condition. The default value is True.
        A 2D cell is regular if and only if there is no repetition in the boundary edges that define the cell.
        By default, the cell is assumed to be regular unless otherwise specified. Self-loops are not allowed in the boundary
        of the cell. If a cell violates the cell complex regularity condition, a ValueError is raised.
    **attr : keyword arguments, optional
        Properties belonging to the cell can be added as key-value pairs. Both the key and value must be hashable.

    Notes
    -----
    - A cell is defined as an ordered sequence of nodes (n1, ..., nk), where each two consecutive nodes (ni, ni+1)
    define an edge in the boundary of the cell. Note that the last edge (nk, n1) is also included in the boundary
    of the cell and is used to close the cell. For instance, if a Cell is defined as `c = Cell((1, 2, 3))`,
    then `c.boundary` will return `[(1, 2), (2, 3), (3, 1)]`, which consists of three edges.
    - When cell is created, its boundary is automatically created as a
    set of edges that encircle the cell.

    Examples
    --------
    >>> cell1 = Cell((1, 2, 3))
    >>> cell2 = Cell((1, 2, 4, 5), weight=1)
    >>> cell3 = Cell(("a", "b", "c"))
    >>> # create geometric cell:
    >>> v0 = (0, 0)
    >>> v1 = (1, 0)
    >>> v2 = (1, 1)
    >>> v3 = (0, 1)
    # create the cell with the vertices and edges
    >>> cell = Cell([v0, v1, v2, v3], type="square")
    >>> cell["type"]
    >>> list(cell.boundary)
    [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)),
    ((0, 1), (0, 0))]
    """

    def __init__(
        self, elements: Collection, name: str = "", regular: bool = True, **attr
    ) -> None:
        super().__init__(tuple(elements), name, **attr)

        self._regular = regular
        elements = list(elements)
        self._boundary = list(
            zip_longest(elements, elements[1:] + [elements[0]])
        )  # list of edges defines the boundary of the 2d cell
        if len(elements) <= 1:
            raise ValueError(
                f"cell must contain at least 2 edges, got {len(elements)+1}"
            )

        if regular:
            _adjdict = {}
            for e in self._boundary:
                if e[0] in _adjdict:
                    raise ValueError(
                        f" Node {e[0]} is repeated multiple times in the input cell."
                        + " Input cell violates the cell complex regularity condition."
                    )
                _adjdict[e[0]] = e[1]
        else:
            for e in self._boundary:
                if e[0] == e[1]:
                    raise ValueError(
                        f"self loops are not permitted, got {(e[0],e[1])} as an edge in the cell's boundary"
                    )

    def clone(self) -> "Cell":
        """Clone the Cell with all properties.

        The clone method by default returns an independent shallow copy of the cell and attributes. That is, if an
        attribute is a container, that container is shared by the original and the copy. Use Python’s `copy.deepcopy`
        for new containers.

        Returns
        -------
        Cell
        """
        return Cell(self.elements, self.name, self._regular, **self._properties)

    @staticmethod
    def is_valid_cell(elements: Sequence, regular: bool = False) -> bool:
        """Check if a 2D cell defined by a list of elements is valid.

        Parameters
        ----------
        elements : Sequence
            List of elements defining the cell.
        regular : bool, default=False
            Indicates if the cell is regular.

        Returns
        -------
        bool
            True if the cell is valid, False otherwise.
        """
        _boundary = list(
            zip_longest(elements, elements[1:] + [elements[0]])
        )  # list of edges define the boundary of the 2d cell
        if len(elements) <= 1:
            return False

        if regular:
            _adjdict = {}
            for e in _boundary:
                if e[0] in _adjdict:
                    return False

                _adjdict[e[0]] = e[1]
        else:

            for e in _boundary:
                if e[0] == e[1]:
                    return False
        return True

    @property
    def is_regular(self) -> bool:
        """Check if a cell is regular.

        Returns
        -------
        bool
            True if the Cell is regular, and False otherwise
        """
        if self._regular:  # condition enforced
            return True
        else:
            _adjdict = {}
            for e in self._boundary:
                if e[0] in _adjdict:
                    return False
                _adjdict[e[0]] = e[1]

        return True

    def sign(self, edge) -> Literal[-1, 1]:
        """Compute the sign of the edge with respect to the cell.

        This takes an edge as input and computes the sign of the edge with respect to the cell.

        If the edge is in the boundary of the cell, then the sign is 1 if the edge is in the
        counterclockwise direction around the cell and -1 if it is in the clockwise direction.

        If the edge is not in the boundary of the cell, a KeyError is raised.

        Parameters
        ----------
        edge: an iterable representing the edge whose sign with respect to the cell is to be computed.

        Returns
        -------
        1: if the edge is in the boundary of the cell and is in the counterclockwise direction around the cell.
        -1: if the edge is in the boundary of the cell and is in the clockwise direction around the cell.

        Raises
        ------
        KeyError
            If the input edge is not in the boundary of the cell.
        ValueError
            If the input edge is not valid.
        TypeError
            If the input edge is not an iterable.
        """
        if not isinstance(edge, Iterable):
            raise TypeError(f"The input {edge} must be iterable.")

        if len(edge) == 2:
            if tuple(edge) in self.boundary:
                return 1
            elif tuple(edge)[::-1] in self.boundary:
                return -1
            else:
                raise KeyError(f"the input {edge} is not in the boundary of the cell")

        raise ValueError(f"The input {edge} is not a valid edge")

    def __repr__(self) -> str:
        """Return string representation of regular cell."""
        return f"Cell({self.elements})"

    @property
    def boundary(self):
        """Boundary.

        A 2d cell is characterized by its boundary edges.

        Returns
        -------
        Iterator of tuple representing boundary edges given in cyclic order.
        """
        return iter(self._boundary)

    def reverse(self):
        """Reverse the sequence of nodes that defines the cell.

        Returns
        -------
        Cell
            New cell with the new reversed elements.
        """
        return Cell(
            self.elements[::-1],
            name=self.name,
            regular=self._regular,
            **self._properties,
        )

    def is_homotopic_to(self, cell) -> bool:
        """Check if self is homotopic to input cell.

        Parameters
        ----------
        cell : tuple, list or Cell

        Returns
        -------
        bool
            Return True is self is homotopic to input cell and False otherwise.
        """
        return Cell._are_homotopic(self, cell) or Cell._are_homotopic(
            self.reverse(), cell
        )

    @staticmethod
    def _are_homotopic(cell1, cell) -> bool:
        """Check if cell1 is homotopic to input cell.

        Parameters
        ----------
        cell1 : Cell
        cell : tuple, list or Cell

        Returns
        -------
        return True is self is homotopic to input cell and False otherwise.

        Notes
        -----
        in a 2d-cell complex, two 2d-cells are homotopic iff one
            of them can be obtaine from the other by a cylic rotation
            of the boundary verties defining the 2d cells.
        """
        if isinstance(cell, tuple) or isinstance(cell, list):
            seq = cell
        elif isinstance(cell, Cell):
            seq = cell.elements
        else:
            raise TypeError(
                "fInput {cell} must be a tuple/list of nodes defining a cell or Cell"
            )

        if not isinstance(cell1, Cell):
            raise TypeError("first argument cell must be a cell")

        if len(cell1) != len(cell):
            return False

        mset1 = Counter(seq)
        mset2 = Counter(cell1.elements)
        if mset1 != mset2:
            return False

        size = len(seq)
        deq1 = deque(cell1.elements)
        deq2 = deque(seq)
        for _ in range(size):
            deq2.rotate()
            if deq1 == deq2:
                return True
        return False

    def __str__(self) -> str:
        """Return string representation of regular cell."""
        return f"Nodes set:{self.elements}, boundary edges:{self.boundary}, attrs:{self._properties}"
