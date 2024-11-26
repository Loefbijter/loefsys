How to Write Docstring Documentation
====================================

In principle, all code in the repository needs to be sufficiently tested and documented. This section covers how to write proper documentation.

For the style of docstrings, the Numpy style is used. Therefore, refer to the `Numpy Style Guide`_ when writing docstrings.

Examples
--------

Module Example
^^^^^^^^^^^^^^
See the `Numpy Style Guide`_ for reference on writing module docstrings.

.. code-block:: python

    """Write a short, one-line summary here.

    After a blank line, continue with a more elaborate description. Optionally include
    exported classes and functions and/or usage examples.
    """

Function Example
^^^^^^^^^^^^^^^^

See the `Numpy Style Guide`_ for reference on writing function docstrings.

.. code-block:: python

    def foo(bar: str, baz: int) -> str:
        """Write a short, one-line summary here

        If necessary, write a somewhat more extensive summary here. This can be as long
        as necessary.

        Parameters
        ----------
        bar : str
            This is the description of parameter `bar`.
        baz : int
            This is the description of parameter `baz`.

        Returns
        -------
        str
            Description of the return value.
        """
        return "Hello world!"

Class Example
^^^^^^^^^^^^^

See the `Numpy Style Guide`_ for reference on writing class docstrings.

.. code-block:: python

    class Foo:
        """Again, write a short, one-line summary of the class

        Follow with longer class information.

        Attributes
        ----------
        bar : int
            This is the description of parameter `bar`.
        """

        bar: int

        def __init__(self):
            """Initialize the Foo instance.

            Can't be bothered to write more.
            """
            self.bar = 0

.. _Numpy Style Guide: https://numpydoc.readthedocs.io/en/latest/format.html
