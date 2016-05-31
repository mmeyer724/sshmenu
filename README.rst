sshmenu
-------
``sshmenu`` is a simple tool for connecting to remote hosts via ssh. Great if you have trouble remembering ip addresses, hostnames, or usernames.

This tool works by using Python's ``os.execvp(...)``, which will replace the current process (python) with ``ssh``.

.. image:: http://i.imgur.com/X1jaoci.gif


Installation
------------
Tested working on OS X El Capitan (10.11.5) and Ubuntu Trusty Tahr (14.04), Xenial Xerus (16.04)


**OS X**

.. code-block:: bash

   brew install https://raw.githubusercontent.com/Mike724/sshmenu/master/sshmenu.rb
   
**Linux**

.. code-block:: bash

   pip3 install sshmenu

Configuration
-------------
On first run an example configuration file will be created for you, along with the path. For reference, I've added this information here as well.

**OS X**

.. code-block:: bash

   nano ~/Library/Application\ Support/sshmenu/config.json
   
**Linux**

.. code-block:: bash

   nano ~/.config/sshmenu/config.json

**Default contents**

.. code-block:: json

    {
        "targets": [
            {
                "host": "user@example-machine.local",
                "friendly": "This is an example target",
                "options": []
            }
        ]
    }

You can specify additional command line options (see `man ssh`) as follows:

.. code-block:: json
    
    {
        "targets": [
            {
                "host": "user@example-machine.local",
                "friendly": "An example target listening non-standard port and verbose flag", 
                "options" : [
                    "-p443",
                    "-v"
                ]
            }
        ]
    }

Todo
----
* Automatically ask to place your ``~/.ssh/id_rsa.pub`` into the remote host's ``~/.ssh/authorized_keys``
