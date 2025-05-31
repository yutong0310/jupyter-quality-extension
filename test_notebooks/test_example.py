#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import math
import os
import numpy as np


# In[2]:


def square(x):
    return x * x


# In[ ]:


def classify_number(n):
    if n > 0:
        return "positive"
    elif n < 0:
        return "negative"
    else:
        return "zero"


# In[ ]:


assert classify_number(5) == "positive"
assert classify_number(-3) == "negative"
assert classify_number(0) == "zero"


# In[3]:


results = []
for i in range(5):
    results.append(square(i))
print(results)


# In[ ]:


def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y

