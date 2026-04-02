Installation
============

PyPI (pip) is the recommended way to install *sqlalchemyobjects*, but GitHub can also be used. If you want to run the examples
and Jupyter tutorials included in this repository, you should clone and install from GitHub.


PyPI
----
You can install sqlalchemyobjects using pip:

.. code-block:: bash

   pip install sqlalchemyobjects


GitHub
------

Install the latest code from the main branch without cloning:

.. code-block:: bash

   pip install "git+https://github.com/AnthonyTechnologies/python-sqlalchemyobjects.git@main"


GitHub Clone
------------

Installing a GitHub clone can be useful for either exploring the examples and tutorials or contributing to
*sqlalchemyobjects*.

For only exploring examples and tutorials:

.. code-block:: bash

   git clone https://github.com/AnthonyTechnologies/python-sqlalchemyobjects.git
   cd python-sqlalchemyobjects
   pip install .[jupyter]

For contributing to or developing *sqlalchemyobjects*:

.. code-block:: bash

   git clone https://github.com/AnthonyTechnologies/python-sqlalchemyobjects.git
   cd python-sqlalchemyobjects
   pip install -e .[dev]
