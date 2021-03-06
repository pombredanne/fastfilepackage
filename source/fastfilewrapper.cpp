//https://docs.python.org/3/c-api/intro.html#include-files
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "version.h"
#include "installation_options.h"
#include "fastfile.cpp"

typedef struct
{
    PyObject_HEAD
    FastFile* cppobjectpointer;
}
PyFastFile;

// https://gist.github.com/physacco/2e1b52415f3a964ad2a542a99bebed8f
// https://stackoverflow.com/questions/48786693/how-to-wrap-a-c-object-using-pure-python-extension-api-python3
static PyModuleDef fastfilepackagemodule =
{
    // https://docs.python.org/3/c-api/module.html#c.PyModuleDef
    PyModuleDef_HEAD_INIT,
    "fastfilepackage", /* name of module */
    "An module written with pure Python C Extensions to open a file and cache the more recent accessed lines", /* module documentation, may be NULL */
    -1, /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    NULL, /* PyMethodDef* m_methods */
    NULL, /* inquiry m_reload */
    NULL, /* traverseproc m_traverse */
    NULL, /* inquiry m_clear */
    NULL, /* freefunc m_free */
};

// initialize PyFastFile Object
static int PyFastFile_init(PyFastFile* self, PyObject* args, PyObject* kwargs) {
    char* filepath;
    char* rawregex;

    char empty[] = "";
    static char* kwlist[] = { empty, empty, NULL };

    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "s|s", kwlist, &filepath, &rawregex ) ) {
        return -1;
    }

    FastFile* fast = new FastFile( filepath, rawregex );
    self->cppobjectpointer = fast;
    return 0;
}

// destruct the object
static void PyFastFile_dealloc(PyFastFile* self)
{
    // https://stackoverflow.com/questions/56212363/should-i-call-delete-or-py-xdecref-for-a-c-class-on-custom-dealloc-for-python
    delete self->cppobjectpointer;
    Py_TYPE(self)->tp_free( (PyObject*) self );
}

static PyObject* PyFastFile_tp_call(PyFastFile* self, PyObject* args, PyObject *kwargs)
{
    PyObject* returnvalue = (self->cppobjectpointer)->call();
    Py_INCREF( returnvalue );
    return returnvalue;
}

static PyObject* PyFastFile_tp_iter(PyFastFile* self, PyObject* args)
{
    Py_INCREF( self );
    return (PyObject*) self;
}

static PyObject* PyFastFile_iternext(PyFastFile* self, PyObject* args)
{
    if( !( (self->cppobjectpointer)->next() ) ) {
        // uncomment this to see why this function is stopping
        // PyErr_Print();
        // PyErr_Clear();
        // PyErr_SetNone( PyExc_StopIteration );
        return NULL;
    }

    PyObject* returnvalue = (self->cppobjectpointer)->call();
    Py_INCREF( returnvalue );
    return returnvalue;
}

static PyObject* PyFastFile_getlines(PyFastFile* self, PyObject* args)
{
    std::string returnvalue;
    unsigned int linestoget;

    if( !PyArg_ParseTuple( args, "i", &linestoget ) ) {
        return NULL;
    }
    // https://stackoverflow.com/questions/36098984/python-3-3-c-api-and-utf-8-strings
    returnvalue = (self->cppobjectpointer)->getlines( linestoget );
    return PyUnicode_DecodeUTF8( returnvalue.c_str(), returnvalue.size(), "replace" );
}

static PyObject* PyFastFile_resetlines(PyFastFile* self, PyObject* args)
{
    (self->cppobjectpointer)->resetlines();
    Py_INCREF( Py_None );
    return Py_None;
}

static PyObject* PyFastFile_close(PyFastFile* self, PyObject* args)
{
    (self->cppobjectpointer)->close();
    Py_INCREF( Py_None );
    return Py_None;
}

static PyMethodDef PyFastFile_methods[] =
{
    { "close", (PyCFunction) PyFastFile_close, METH_VARARGS, "If the file object was open, close it" },
    { "getlines", (PyCFunction) PyFastFile_getlines, METH_VARARGS, "Return a string with `nth` cached lines" },
    { "resetlines", (PyCFunction) PyFastFile_resetlines, METH_NOARGS, "Reset the current line counter" },
    { "line", (PyCFunction) PyFastFile_tp_call, METH_NOARGS, "Return the next line or an empty string on the file end" },
    { "next", (PyCFunction) PyFastFile_iternext, METH_NOARGS, "Advances the iterator to the next line" },
    { NULL, NULL, 0, NULL }  /* Sentinel */
};

static PyTypeObject PyFastFileType =
{
    PyVarObject_HEAD_INIT( NULL, 0 )
    "fastfilepackage.FastFile" /* tp_name */
};

// create the module
PyMODINIT_FUNC PyInit_fastfilepackage(void)
{
    PyObject* thismodule;

    // https://docs.python.org/3/c-api/typeobj.html
    PyFastFileType.tp_call = (ternaryfunc) PyFastFile_tp_call;
    PyFastFileType.tp_iter = (getiterfunc) PyFastFile_tp_iter;
    PyFastFileType.tp_iternext = (iternextfunc) PyFastFile_iternext;

    PyFastFileType.tp_new = PyType_GenericNew;
    PyFastFileType.tp_basicsize = sizeof(PyFastFile);
    PyFastFileType.tp_dealloc = (destructor) PyFastFile_dealloc;
    PyFastFileType.tp_flags = Py_TPFLAGS_DEFAULT;
    PyFastFileType.tp_doc = "FastFile objects";

    PyFastFileType.tp_methods = PyFastFile_methods;
    // PyFastFileType.tp_members = PyFastFile_members;
    PyFastFileType.tp_init = (initproc) PyFastFile_init;

    if( PyType_Ready( &PyFastFileType) < 0 ) {
        return NULL;
    }

    thismodule = PyModule_Create(&fastfilepackagemodule);

    if( thismodule == NULL ) {
        return NULL;
    }

    // https://docs.python.org/3/c-api/arg.html#c.Py_BuildValue
    // https://stackoverflow.com/questions/3001239/define-a-global-in-a-python-module-from-a-c-api
    PyObject_SetAttrString( thismodule, "__version__", Py_BuildValue( "s", __version__ ) );
    PyObject_SetAttrString( thismodule, "FASTFILE_TRIMUFT8", Py_BuildValue( "i", FASTFILE_TRIMUFT8_CONSTANT ) );

    // Add FastFile class to thismodule allowing the use to create objects
    Py_INCREF( &PyFastFileType );
    PyModule_AddObject( thismodule, "FastFile", (PyObject*) &PyFastFileType );
    return thismodule;
}
