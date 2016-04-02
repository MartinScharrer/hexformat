======
How-to
======

Basic actions
=============
The following methods are defined in the base class :class:`.MultiPartBuffer` and are available with all hexformat
classes.

Load an existing file
---------------------
Methods are provided to read the data from already opened file handles (or compatibles) or by providing the file name
only.

A new instance can be directly created from using :meth:`.fromfh` and :meth:`.fromfile`.
These methods will use the default format and call ``from<formatname>fh()`` and ``from<formatname>file()`` respectively.
All classes support reading from binary files using :meth:`.frombinfh` and :meth:`.frombinfile`

Additional content can be read to an exising instance using :meth:`.loadfh` and :meth:`.loadfile`.
These methods will use the default format and call ``load<formatname>fh()`` and ``load<formatname>file()`` respectively.
All classes support reading from binary files using :meth:`.loadbinfh` and :meth:`.loadbinfile`

Create new instance from binary file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: hexformat.multipartbuffer.MultiPartBuffer.frombinfh
    :noindex:

.. automethod:: hexformat.multipartbuffer.MultiPartBuffer.frombinfile
    :noindex:

Example::

    from hexformat.srecord import SRecord
    srec = SRecord.frombinfile("somefile.bin")
    with open("somefile.bin", "rb") as fh:
        srec2 = SRecord.frombinfh(fh)


Load (more) content from a binary file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: hexformat.multipartbuffer.MultiPartBuffer.loadbinfh
    :noindex:

.. automethod:: hexformat.multipartbuffer.MultiPartBuffer.loadbinfile
    :noindex:

Example::

    from hexformat.srecord import SRecord
    srec = SRecord()
    srec.loadbinfile("somefile.bin")
    with open("somefile.bin", "rb") as fh:
        srec = SRecord.loadbinfh(fh)


Create new instance from hex file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
These methods are using the standard format of the class as long no other is specified using the `fformat` argument.

.. automethod:: hexformat.multipartbuffer.MultiPartBuffer.fromfh
    :noindex:

.. automethod:: hexformat.multipartbuffer.MultiPartBuffer.fromfile
    :noindex:

Example::

    from hexformat.srecord import SRecord
    srec = SRecord.fromfile("somefile.bin")
    with open("somefile.bin", "rb") as fh:
        srec2 = SRecord.fromfh(fh)


Load (more) content from a hex file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
These methods are using the standard format of the class as long no other is specified using the `fformat` argument.

.. automethod:: hexformat.multipartbuffer.MultiPartBuffer.loadfh
    :noindex:

.. automethod:: hexformat.multipartbuffer.MultiPartBuffer.loadfile
    :noindex:

Example::

    from hexformat.srecord import SRecord
    srec = SRecord()
    srec.loadfile("somefile.bin")
    with open("somefile.bin", "rb") as fh:
        srec = SRecord.loadfh(fh)
