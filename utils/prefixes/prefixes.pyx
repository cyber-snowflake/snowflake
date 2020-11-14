from libcpp.unordered_map cimport unordered_map
from libcpp cimport bool as cppbool


cdef unordered_map[int, char*] prefixes

cdef cppbool find(int x):
    cdef cppbool found = False

    for k, v in prefixes:
        if found:
            break

        if k == x:
            found = True

    return found


cpdef void set_prefix(int _id, char* new_prefix):
    prefixes[_id] = new_prefix

cpdef char* get_prefix(int _id):
    if find(_id):
        return prefixes[_id]
    else:
        raise ValueError(f"There's no value for {_id}")

