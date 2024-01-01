from dataclasses import dataclass

def check_state(func):
    """
    Checks whether or not _state_
    has only a single bit on.
    """
    
    def wrapper(*args, **kwargs):
        state = args[1]                 # arg 1 is self
        assert (state & (state-1) == 0), "BitSet: Invalid state"
        return func(*args, **kwargs)

    return wrapper

@dataclass
class BitSet:
    field = 0

    def __init__(self, field=0):
        self.field = field
    
    @check_state
    def set(self, state):
        """
        state -> an ElemState enum
        """
        if not self.test(state):
            self.field |= state

    @check_state
    def clear(self, state):
        if self.test(state):
            self.field &= ~state
    
    @check_state
    def test(self, state):
        return self.field & state
    
    @check_state
    def flip(self, state):
        """
        Sets a bit (state) if it isn't set,
        and clears it otherwise.
        """
        if self.test(state):
            self.clear(state)
        else:
            self.set(state)


