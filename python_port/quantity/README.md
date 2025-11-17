# Quantity utilities in Python

This package contains Python-friendly reimplementations of the C++ classes in
`src/FoundationClasses/TKernel/Quantity`.  The goal is to make the small
numerical helpers easier to inspect or test without compiling OCCT.

## `period.py`

`period.py` ports `Quantity_Period` from
`src/FoundationClasses/TKernel/Quantity/Quantity_Period.hxx/.cxx`.  The Python
version keeps the same method names (`set_values`, `is_shorter`, `add`, ...)
so that reading the original C++ source alongside the port is straightforward.
