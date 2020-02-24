from itertools import filterfalse, tee


def partition(pred, iterable):
    """Partition an iterable into two iterables based on a predicate

    Ex: Use a predicate to partition entries into false entries and true entries
    partition(is_odd, range(10)) --> 0 2 4 6 8  and  1 3 5 7 9

    Args:
       pred (v -> bool): A predicate that takes values in the iterable to true and false
       iterable (iter(v)): An iterable of values of type v

    Returns:
       true_iter (iter(v)):  Iterator of values in iterable where predicate evaulates to True
       false_iter (iter(v)): Iterator of values in iterable where predicate evaluates to False
    """
    true_iter, false_iter = tee(iterable)
    return filter(pred, true_iter), filterfalse(pred, false_iter)


def partition_list(pred, iterable):
    """Paritions an iterable into two lists of values

    This tools works the same way as partition except that it
    immediately splits the values in the iterable into two lists,
    instead of returning two iterators that partition as they go. This
    is useful when the values that are being parttitioned on can
    change at any time, hence values could be lost by the iterable
    version or counted twice.

    Args:
       pred (v -> bool): A predicate that takes values in the iterable to true and false
       iterable (iter(v)): An iterable of values of type v

    Returns:
       true_list (list(v)):  Iterator of values in iterable where predicate evaulates to True
       false_list (list(v)): Iterator of values in iterable where predicate evaluates to False

    """
    true_list = []
    false_list = []
    for item in iterable:
        if pred(item):
            true_list.append(item)
        else:
            false_list.append(item)
    return true_list, false_list
