===================
Developer Reference
===================

Cloning and Setup
-----------------

You should always develop in a virtual environment (we *strongly* recommend using something like
pyenv_, with pyenv-virtualenv_ which are installable with brew_), and you should always test against Python 3.8+
(see :ref:`testing`). In your virtual environment use the following pip command to install requirements from)
within the scdatatools directory. For your convenience, this would be a common set of commands to setup a dev
environment:

.. code-block:: bash

    git clone https://github.com/ExterraGroup/scdatatools
    cd scdatatools
    pyenv install 3.8.2
    pyenv virtualenv 3.8.2 sc
    pyenv local sc
    pip install -r dev/requirements.txt

`dev/requirements.txt` will also `pip install -e .`. This will install an editable version of scdatatools in
your virtual environment so changes you make in the repository will be reflected immediately without having to reinstall
the package.

.. _testing:

Testing
-------

`scdatatools` tests are implemented using unittest and can easily be run using the `nosetests` command.

.. code-block:: bash

    nosetests --with-coverage --cover-package scdatatools --cover-html


API Reference
-------------

.. toctree::
    :maxdepth: 5

    api/modules


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`


.. _pyenv: https://github.com/pyenv/pyenv
.. _pyenv-virtualenv: https://github.com/pyenv/pyenv-virtualenv
.. _brew: https://brew.sh/
