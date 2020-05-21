===========
scdatatools
===========


.. image:: https://img.shields.io/pypi/v/scdatatools.svg
        :target: https://pypi.python.org/pypi/scdatatools

.. image:: https://img.shields.io/travis/ExterraGroup/scdatatools.svg
        :target: https://travis-ci.org/ExterraGroup/scdatatools

.. image:: https://readthedocs.org/projects/scdatatools/badge/?version=latest
        :target: https://scdatatools.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/ExterraGroup/scdatatools/badge.svg?branch=devel
        :target: https://coveralls.io/github/ExterraGroup/scdatatools?branch=devel

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black


Python API for interactive with the data files in Star Citizen.

.. warning:: This toolsuite is in it's very early stages and will change often.

* Free software: MIT license
* Documentation: https://scdatatools.readthedocs.io.

Hey! Listen!
------------

This tool is in **very** early development. The CLI is a WIP and may not be completely plumbed up yet.
If you'd like to help out and know Python, try out the API a little bit and see if you run into errors parsing
files! We're also at the stage that feature/usability feedback would be much appreciated.


Features
--------

* cli interface
* TODO


CLI Examples
------------

.. code-block:: bash

    scdt --help
    usage: scdt [-h] [--verbose] [--stderr] [--command-timeout COMMAND_TIMEOUT] [command] ...

    positional arguments:
      [command]             Subcommand to run, if missing the interactive mode is started instead.
        cryxml-to-json      Convert a CryXML file to JSON
        cryxml-to-xml       Convert a CryXML file to xml
        unforge             Convert a DataForge file to a readable format
        unp4k               Extract files from a P4K file

API Examples
------------

Read a DataForge database (.dcb)

.. code-block:: bash

    from scdatatools.forge import DataCoreBinary
    dcb = DataCoreBinary('research/Game.dcb.3.9.1-ptu.5229583')
    jav_records = dcb.search_filename('*javelin.xml')
    print(dcb.dump_record_json(jav_records[-1]))


Special Thanks
--------------

A huge thanks goes out to `dolkensp <https://github.com/dolkensp/unp4k>`_ (aka alluran) for doing all the initial hard
work reversing the P4K and DataForge file formats! This would've taken a lot longer with his efforts.
