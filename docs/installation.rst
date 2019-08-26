============
Installation
============

You can install the package from PyPI using this command:

.. code-block:: bash

    pip install -U bpptkg-richter

You can also install the package from our GitLab repository. Download the latest
version from GitLab repository and unpack the archive:

.. code-block:: bash

    tar -xvf bpptkg-richter-v<major>.<minor>.<patch>.tar.gz

Where ``major``, ``minor``, and ``patch`` are package semantic versioning
number. Then, make Python virtual environment and activate the virtual
environment:

.. code-block:: bash

    virtualenv -p python3 venv
    source venv/bin/activate

Install dependency packages:

.. code-block:: bash

    cd /path/to/bpptkg-richter/
    pip install -r requirements.txt

Install the package:

.. code-block:: bash

    pip install -e .
