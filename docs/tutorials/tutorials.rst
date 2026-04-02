Tutorials and Examples
======================

.. contents:: Contents
   :local:
   :backlinks: none

This project includes additional tutorials and examples in the repository to help you learn by doing.

Jupyter Tutorials
-----------------

The following Jupyter notebooks are available in the ``tutorials/`` directory of the repository:

*   ``tutorials/database_tutorial.ipynb``: A deep dive into the ``Database`` class, connection management, and sessions.
*   ``tutorials/tables/base/basetable_tutorial.ipynb``: A getting started guide covering basic table definition and CRUD operations.
*   ``tutorials/tables/base/extending_tables_search_filter_tutorial.ipynb``: Learn how to implement custom query logic and advanced filters in your manifestations.
*   ``tutorials/tables/base/run_runtime_search_filter_tutorial.ipynb``: Learn how to run searches and filters on tables at runtime without extending classes.
*   ``tutorials/tables/base/singletontable_tutorial.ipynb``: A guide on using singleton tables for configuration management.
*   ``tutorials/tables/base/metainformationtable_tutorial.ipynb``: Learn how to manage cached application metadata.
*   ``tutorials/tables/base/updatetable_tutorial.ipynb``: Track sequential updates and perform delta queries.

To run the notebooks locally, install the optional dependencies and launch Jupyter:

.. code-block:: bash

   pip install -e .[jupyter]
   jupyter notebook tutorials/

Note: The documentation site does not render the notebooks directly.

Code Examples
-------------

The ``examples/`` directory in the repository contains several Python scripts demonstrating key features of the
package. These are great for seeing how the various components work together in a complete application.

Basic Examples
~~~~~~~~~~~~~~

*   ``examples/database_example.py``: Shows how to define and use the ``Database`` object for basic operations.
*   ``examples/tables/base/basetable_example.py``: A detailed example of defining schemas, manifestations, and using
    both synchronous and asynchronous CRUD methods.

Advanced Examples
~~~~~~~~~~~~~~~~~

*   ``examples/comprehensive_example.py``: A large-scale example demonstrating complex database structures,
    inheritance, and a wide range of CRUD operations.
*   ``examples/tables/base/singletontable_example.py``: Demonstrates the ``SingletonTable``, which is useful for tables
    that should only ever have one row (e.g., global configuration).
*   ``examples/tables/base/metainformationtable_example.py``: Shows how to use the ``MetaInformationTable`` for
    storing key-value pairs of metadata.
*   ``examples/tables/base/updatetable_example.py``: Demonstrates the ``UpdateTable``, which provides built-in
    mechanisms for tracking when rows were last updated.

Running the Examples
~~~~~~~~~~~~~~~~~~~~

You can run these examples directly from the repository. Most of them use an in-memory or temporary SQLite database,
so no external setup is required.

.. code-block:: bash

   python examples/database_example.py
   python examples/tables/base/basetable_example.py
