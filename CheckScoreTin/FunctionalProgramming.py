from functools import *
from itertools import *

def iterate(f, x):
  # Return [ x, f(x), f(f(x)), ...]
  # Input : f is a function with single argument that you want to iterate, x is initial value of argument
  # Output: sequence of x, f(x), f(f(x))
  return accumulate(repeat(x), lambda fx, _: f(fx))

def ConditionToStopIterationForSearchString(prev, curr):
    # Interrupt Iterations when condition is happenning, more specificly when current value = -1
    # Input: prev is previous value, curr is current value, they can be given by fuctions 'repeat' or 'iterate'
    # Output: return current value
    if curr == -1: raise StopIteration
    else: return curr