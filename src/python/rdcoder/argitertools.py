
# TYPING
# ------

from typing import Callable as _Callable, Iterable as _Iterable, Hashable as _Hashable
from typing import Dict as _Dict, List as _List
_Runnable = _Callable[[], None]
_Predicate = _Callable[[], bool]
_Mapper = _Callable[[_Hashable], _Hashable]

# INDEXING TOOLS
# --------------

def argsmatch(
    iterable: _Iterable[_Hashable], mapfunc: _Mapper,
    only_matches: bool = True
) -> _Dict[_Hashable, _Dict[str, _List[int] | None]]:
    ''' Groups by index elements that are equal when mapped.

    Returns a dict where a key is an item from {iterable} and its value
    is a subdict with two indices lists, where:
    - "argsequal" is a list of indices where key can be found in {iterable};
    - "argsmatch" is a list of indices whose items matches the mapping of key
    performed with the mapper function {mapfunc} or None if no matches were found.
    
    Items are compared based on their hashes, thus elements within {iterable}
    as well as the value returned by {mapfunc} must be hashable.

    The item's index starts at zero and is incremented as the {iterable} is
    consumed. If you want to track the position of the items in iterable,
    make sure to cast it to a sequeanceable type before pass to this function
    since it has deterministic positions.

    Parameters
    ----------
    iterable : _Iterable[Hashable]
        The iterable that contains the items to be grouped.
    mapfunc : _Mapper
        The mapping function.
    only_matches : bool
        If true (by default), only items that have at least one match will be
        put in the returned dict and subsequent matches will be excluded from it.
        About the latter, note that the 'argsmatch' of an item is the 'argsequal'
        of its map, so no information is lost.

    Usage
    -----
    For example, if we have a list of numbers and want to group indices of items
    that are the exact opposite, we can pass a mapping function that inverts the
    sign of the item.

        argswhere([1, -1, 2, -1, 1], lambda number: -number, only_matches = False)
        
    return will be:

        {
            1: { 'argsequal': [0, 4], 'argsmatch': [1, 3] },
            -1: { 'argsequal': [1, 3], 'argsmatch': [0, 4] },
            2: { 'argsequal': [2], 'argsmatch': None }
        }

    If {only_matches} is True the item 2 is not put to the dict because the
    list doesn't contain -2, neither -1 because its opposite already exists.
    '''
    ARGSEQUAL_KEY = 'argsequal'
    ARGSMATCH_KEY = 'argsmatch'

    items = dict()
    matcheditems = dict() if only_matches else items

    index = 0
    for item in iterable:
        # 1: Puts index of item to items
        item_in_items = item in items
        if item_in_items:
            item_val = items[item]
            item_val[ARGSEQUAL_KEY].append(index)
        else:
            items[item] = item_val = {ARGSEQUAL_KEY: [index], ARGSMATCH_KEY: None}

        # 2: Puts index of item to the mapped match 
        mappeditem = mapfunc(item)
        if mappeditem in items:
            mappeditem_val = items[mappeditem]
            # Call items[item] here is safe because is guaranteed that item was
            # put to items if that statement is called after block 1.
            mappeditem_val[ARGSMATCH_KEY] = item_val[ARGSEQUAL_KEY]
            if not item_in_items:
                matcheditems[mappeditem] = mappeditem_val
        
        index+=1

    return matcheditems