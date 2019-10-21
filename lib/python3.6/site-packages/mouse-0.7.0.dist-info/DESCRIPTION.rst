mouse
=====

Take full control of your mouse with this small Python library. Hook
global events, register hotkeys, simulate mouse movement and clicks, and
much more.

*Huge thanks to `Kirill Pavlov <http://kirillpavlov.com/>`__ for
donating the package name. If you are looking for the Cheddargetter.com
client implementation,
```pip install mouse==0.5.0`` <https://pypi.python.org/pypi/mouse/0.5.0>`__.*

Features
--------

-  Global event hook on all mice devices (captures events regardless of
   focus).
-  **Listen** and **sends** mouse events.
-  Works with **Windows** and **Linux** (requires sudo).
-  **Pure Python**, no C modules to be compiled.
-  **Zero dependencies**. Trivial to install and deploy, just copy the
   files.
-  **Python 2 and 3**.
-  Includes **high level API** (e.g. `record <#mouse.record>`__ and
   `play <#mouse.play>`__.
-  Events automatically captured in separate thread, doesn't block main
   program.
-  Tested and documented.

This program makes no attempt to hide itself, so don't use it for
keyloggers.

Usage
-----

Install the `PyPI package <https://pypi.python.org/pypi/mouse/>`__:

::

    $ sudo pip install mouse

or clone the repository (no installation required, source files are
sufficient):

::

    $ git clone https://github.com/boppreh/mouse

Then check the `API docs <https://github.com/boppreh/mouse#api>`__ to
see what features are available.

Known limitations:
------------------

-  Events generated under Windows don't report device id
   (``event.device == None``).
   `#21 <https://github.com/boppreh/keyboard/issues/21>`__
-  To avoid depending on X the Linux parts reads raw device files
   (``/dev/input/input*``) but this requries root.
-  Other applications, such as some games, may register hooks that
   swallow all key events. In this case ``mouse`` will be unable to
   report events.


