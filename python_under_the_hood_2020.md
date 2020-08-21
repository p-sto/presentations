Python under the hood
=====================

Objects, names, binding
---

```python
>>> class Foo:
...    pass

>>> Foo()       # object creation
>>> bar = Foo() # object bound to name 'bar'
```

Id, hash
---

```python
>>> id(bar)
>>> hash(bar)       # hash = id(bar) * 4 in default implementation
```

Python's `is` operates on ids.  
Dicts operates on `hash`.  
Not every object has hash (aka `is hashable`), mutable objects (e.g. list) don't
have hashes, immutable - do.

Small integers caching
---
Small integers (-5, 256) are pre cached at interpreter as these numbers
are 'popular'.

```python
>>> x, y = 100, 100
>>> x is y
True
>>> x += 1
>>> y += 1
>>> x is y
True
>>> x, y = 500, 500
>>> x is y
False
```

Ref count
---
```python
>>> import sys

>>> bar = Foo()
>>> sys.getrefcount(bar)
2       # always ref + 1 due to some internal reference
>>> another_name = bar
>>> sys.getrefcount(bar)
3
>>> sys.getrefcount(another_name)       # just another binding pointing to the same object
3
>>> another_name is bar
True
>>> del another_name
>>> sys.getrefcount(bar)
2
>>> sys.getrefcount(baranother_name)
NameError: name 'another_name' is not defined

>>> import copy
>>> another_name = copy.copy 
>>> sys.getrefcount(bar)
2
>>> sys.getrefcount(another_name)
2
>>> another_name is bar
False

>>> import ctypes   # foreign function interface
>>> address = id(bar)
>>> ctypes.c_long.from_address(address).value
1   # ref count without internal reference
>>> del bar
>>> ctypes.c_long.from_address(address).value
0   # but object exists somewhere, only refence was deleted

# Fun fact:
>>> ctypes.c_long.from_address(1405300919241).value     # some random address
Segmentation fault (core dumped)

# ctypes can be dangerous!
>>> a = [1, 2, 3, 4, 5]
>>> id(a)
140215104178008
>>> a = [x for x in a if x > 3]
>>> a
[4, 5]
>>> id(a)
140215104179232

# precached values:
>>> a = 1
>>> ctypes.c_long.from_address(address).value
627
>>> del a
>>> ctypes.c_long.from_address(address).value
626     # should be the same each time we launch fresh interpreter
>>> sys.getrefcount(None)
2522
# now you may know why we compare to None using `is` operator
```

Garbage Collection
---
```python
>>> bar = Foo()
>>> gc.get_referents(bar)
[<class __main__.Foo at 0x7f072b00fae0>, {}]
>>> gc.is_tracked(bar)
True
>>> address = id(bar)
>>> ctypes.cast(address, ctypes.py_object).value
<__main__.Foo instance at 0x7f072afc5950>
>>> ctypes.cast(address, ctypes.py_object).value
<__main__.Foo instance at 0x7f072afc5950>   # still exists!
>>> gc.collect()
0
>>> ctypes.cast(address, ctypes.py_object).value    # we could even retreive this object
(<refcnt 0 at 0x7f072b009560>, 'cast')
>>> ctypes.cast(address, ctypes.py_object).value
(<refcnt 0 at 0x7f072b009518>, 'py_object')
>>> ctypes.cast(address, ctypes.py_object).value
Fatal Python error: GC object already tracked
Aborted (core dumped)
```

PyObject
---

```c
/* Nothing is actually declared to be a PyObject, but every pointer to
 * a Python object can be cast to a PyObject*.  This is inheritance built
 * by hand.  Similarly every pointer to a variable-size Python object can,
 * in addition, be cast to PyVarObject*.
 */
typedef struct _object {
    _PyObject_HEAD_EXTRA
    Py_ssize_t ob_refcnt;
    PyTypeObject *ob_type;
} PyObject;

```
PyObjects acts as a interface.


source:  
https://github.com/python/cpython/blob/master/Include/object.h  
Brief description of Python internal structures:  
https://docs.python.org/3.8/c-api/structures.html

Lists, Dicts, Tuples
---

### List

```python
>>> import sys
>>> my_list = []
>>> sys.getsizeof(my_list)      # Returns size of an object in bytes(1)
72
>>> my_list.append(1)
>>> sys.getsizeof(my_list)
104
>>> my_list.append(1)
>>> sys.getsizeof(my_list)
104
>>> my_list.append(1)
>>> sys.getsizeof(my_list)
104
>>> my_list.append(1)
>>> sys.getsizeof(my_list)
104
>>> my_list.append(1)
>>> sys.getsizeof(my_list)
136
>>> my_list
[1, 1, 1, 1, 1]
>>> my_list.pop()
1
>>> sys.getsizeof(my_list)
136
>>> my_list.pop()
1
>>> sys.getsizeof(my_list)
120

# List pre-allocates some memory to perform fast appends
# Every element occupies 8B of memory - this is size of PyObject pointer
# (1) Works fine for built-ins, doesn't have to for 3rd party
```

List allocation equation:  
![](list_allocation.png)

Explicitly declared list has no over allocation, however, adding any
new element will cause over-allocation:  
```python
>>> my_list = [1, 2, 3]
>>> sys.getsizeof(my_list)
96
>>> my_list.append(4)
>>> sys.getsizeof(my_list)
128
```

source:  
https://github.com/python/cpython/blob/master/Include/listobject.h  
https://github.com/python/cpython/blob/master/Objects/listobject.c#L24

### Dict

```python
>>> import sys
>>> my_dict = {}
>>> sys.getsizeof(my_dict)
280
>>> my_dict['key1'] = 1
>>> sys.getsizeof(my_dict)
280
>>> my_dict['key2'] = 2
>>> sys.getsizeof(my_dict)
280
>>> my_dict['key3'] = 3
>>> sys.getsizeof(my_dict)
280
>>> my_dict['key4'] = 4
>>> sys.getsizeof(my_dict)
280
>>> my_dict['key5'] = 5
>>> sys.getsizeof(my_dict)
280
>>> my_dict['key6'] = 6
>>> sys.getsizeof(my_dict)
1048
```

Dict pre-allocates 8 chunks of memory and grow x4 when is 2/3 full.
If there are more than 50k allocated chunks of memory, then it grow 2x with
every re-allocation, so allocated chunks will be:  
8, 32, 128, 514, 2048, 8192, 32768, 131072, 262133...

### Tuple
Tuples are simple and there's no magic here, since tuple has fixed size
there is magical pre-allocation:

```python
>>> import sys
>>> my_tuple = (1,)
>>> sys.getsizeof(my_tuple)
64
>>> my_tuple = (1, 2)
>>> sys.getsizeof(my_tuple)
72
>>> my_tuple = (1, 2, 3)
>>> sys.getsizeof(my_tuple)
80
```


Frames
---
Python's interpreter works as a stack machine. Code at runtime is represented
by frames, which are operating over virtual stack. At the same time,
frames are just another object! If so, we can access them.


Stack trace
---


Memory allocator
---

dis module
---
Module module allows to analise CPython bytecode. Bytecode is an actual
code which interpreter evaluates:  
```python
>>> import dis
>>> dis.dis(foo)
>>> dis.dis(foo)
  2           0 LOAD_FAST                0 (arg)
              3 RETURN_VALUE        
```

Each instruction (LOAD_FAST, RETURN_VALUE) has an opcode. Definitions
of all opcodes are stored here:  
https://github.com/python/cpython/blob/master/Include/opcode.h

Python's main loop iterates over bytecode and execute specific functions
based on opcode id. You can check Python's main loop implementation here:  
https://github.com/python/cpython/blob/master/Python/ceval.c#L1490

### Resources

[Python source code](https://github.com/python/cpython)  
[Memory Management](https://rushter.com/blog/python-memory-managment/)  
[Python objects sizes](https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python)  
[10 hrs CPython interpreter tutorial](https://pg.ucsd.edu/cpython-internals.htm)  
[Frames visualisation](http://www.pythontutor.com/)  
[CPython Internals - Book](https://realpython.com/products/cpython-internals-book/)  
[Python interpreter consts definitions](https://github.com/python/cpython/blob/master/Include/pyport.h)