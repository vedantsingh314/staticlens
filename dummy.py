# Dummy Python file for static analysis testing

import math


class Calculator:
    def __init__(self, value):
        self.value = value

    def add(self, x):
        if x > 0:
            return self.value + x
        else:
            return self.value

    def multiply(self, x):
        result = 0
        for i in range(x):
            result += self.value
        return result


def complex_function(a, b):
    total = 0

    if a > b:
        total += a
    elif a == b:
        total += a * 2
    else:
        total += b

    while total < 100:
        total += 10

    try:
        value = total / (a - b)
    except ZeroDivisionError:
        value = 0

    return value


def simple_function(x):
    return x * 2
