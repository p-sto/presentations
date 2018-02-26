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
Dicts operates on `hash`

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

Lists, Dicts, Tuples
---

### List

### Dict

### Tuple

Frames
---
They are regular objects!

Stack trace
---

PyObject
---

Memory allocator
---


### Resources

[Memory Management](https://rushter.com/blog/python-memory-managment/)  
[Python objects sizes](https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python)  
[10 hrs CPython interpreter tutorial](https://pg.ucsd.edu/cpython-internals.htm)  
[Frames visualisation](http://www.pythontutor.com/)  