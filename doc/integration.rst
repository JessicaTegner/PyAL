Integrating PyAL
================
PyAL consists of two modules, :mod:`openal`, which is a plain 1:1 API wrapper
around the OpenAL 1.1 specification, and :mod:`openal.audio`, which contains
some high-level audio classes and helper functions, which use the OpenAL
wrapper.

Both modules are implemented in a way that shall make it easy for you to
integrate and deploy them with your own software projects. You can rely on PyAL
as third-party package, so that the user needs to install it before he can use
your software. Alternatively, you can just copy both modules into your project,
shipping them within your own project bundle.

Importing
---------
The :mod:`openal` module relies on an external OpenAL library which it can
access for creating the wrapper functions. This means that the user needs to
have OpenAL installed or that you ship an OpenAL library with your project.

If the user has an OpenAL library installed on the target system, the
:mod:`ctypes` hooks of :mod:`openal` try to find it in the OS-specific standard
locations via :func:`ctypes.util.find_library`. If you are going to ship your
own OpenAL library with the project or can not rely on the standard mechanism
of :mod:`ctypes`, it is also possible to set the environment variable
:envvar:`PYAL_DLL_PATH`, which shall point to the directory of the OpenAL
library.

.. note::

   :envvar:`PYAL_DLL_PATH` is preferred over the standard mechanism. That said,
   if the module finds a OpenAL library in :envvar:`PYAL_DLL_PATH`, it will try
   to use that one in the first place, before using any OpenAL library
   installed on the target system.
   
Let's assume, you ship your own library *OpenAL.dll* within your project
location *fancy_project/third_party*. You can set the environment variable
:envvar:`PYAL_DLL_PATH` before starting Python. ::

   # Win32 platforms
   set PYAL_DLL_PATH=C:\path\to\fancy_project\third_party

   # Unix/Posix-alike environments - bourne shells export
   PYAL_DLL_PATH=/path/to/fancy_project/third_party

   # Unix/Posix-alike environments - C shells setenv PYAL_DLL_PATH
   /path/to/fancy_project/third_party

You also can set the environment variable within Python using
:data:`os.environ`. ::

   os.environ["PYAL_DLL_PATH"] = "C:\\path\\to\\fancy_project\\third_party"
   os.environ["PYAL_DLL_PATH"] = "/path/to/fancy_project/third_party"
  
.. note::

   If you aim to integrate :mod:`openal` directly into your software and do not
   want or are not allowed to change the environment variables, you can
   also change the ``os.getenv("PYAL_DLL_PATH")`` query within the *openal.py*
   file to point to the directory, in which you keep the DLL.



