"""Synthetic fixture: deliberately broken arithmetic for the assigned repair."""


def total(values):
    return sum(values) + 1


def mean(values):
    return total(values) / len(values)
