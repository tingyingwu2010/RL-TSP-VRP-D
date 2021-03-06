import numpy as np


class MinToMaxRestriction:
    '''
    Used for standard restrictions.The signal list follows this order:
    - If no restriction is violated, its called non violation (non_viol_signal = signal_list[0])
    - If the restriction is violated, but the changed amount is greater than zero its a semi violation (semi_viol_signal = signal_list[1])
    - A restriction violation resulting in a changed amount of zero will be interpreted as a full violation (viol_signal = signal_list[2])
    The violation signal can be used to calculate a reward or penalization.
    '''
    def __init__(self, max_restr, min_restr, signal_list):
        self.max_restr = max_restr
        self.min_restr = min_restr

        self.non_viol_signal  = signal_list[0]
        self.semi_viol_signal = signal_list[1]
        self.viol_signal      = signal_list[2]


    def add_value(self, cur_value, value):
    '''
    Adds a specified amount to the current value under the initialzied max restriction.
    '''
        new_value = cur_value + new_value
        
        if new_value <= self.max_restr:
            cur_value = new_value
            # return 1 to signal NO violation
            return cur_value, self.non_viol_signal
        elif cur_value == self.max_restr:
            # return -1 to signal violation
            return cur_value, self.viol_signal
        else:
            return cur_value, self.semi_viol_signal


    def subtract_value(self, cur_value, value):
        '''
        Subtracts a specified amount from the current value under the initialzied min restriction.
        '''
        new_value = cur_value - new_value
        
        if new_value >= self.min_restr:
            cur_value = new_value
            # return 1 to signal NO violation
            return cur_value, self.non_viol_signal
        elif cur_value == self.min_restr:
            # return -1 to signal violation
            return cur_value, self.viol_signal
        else:
            return cur_value, self.semi_viol_signal


class MinRestriction(MinToMaxRestriction):
    '''
    Extension for MinToMaxRestriction class, that excludes the max restriction.
    '''
    def __init__(self, min_restr, signal_list):
        super().__init__(None, min_restr, signal_list)

    def add_value(self, cur_value, value):
        '''
        Overrides the max restriction from the original class to unrestricted max.
        '''
        cur_value += value
        return cur_value, self.non_viol_signal


class MaxRestriction(MinToMaxRestriction):
    '''
    Extension for MinToMaxRestriction class, that excludes the min restriction.
    '''
    def __init__(self, max_restr, signal_list):
        super().__init__(max_restr, None, signal_list)

    def subtract_value(self, cur_value, value):
        '''
        Overrides the min restriction from the original class to unrestricted min.
        '''
        cur_value -= value
        return cur_value, self.non_viol_signal


class DummyRestriction(MinToMaxRestriction):
    '''
    Used when no restrictions are needed. Extension for MinToMaxRestriction class, that excludes both the min and the max restriction
    '''
    def __init__(self, signal_list):
        super().__init__(None, None, signal_list)

    def add_value(self, cur_value, value):
        '''
        Overrides the max restriction from the original class to unrestricted max.
        '''
        cur_value += value
        return cur_value, self.non_viol_signal

    def subtract_value(self, cur_value, value):
        '''
        Overrides the min restriction from the original class to unrestricted min.
        '''
        cur_value -= value
        return cur_value, self.non_viol_signal

def ValueTrace:

    def __init__(self,value_name):
        self.value_name = value_name
        self.cur_signal = 0
        self.cur_value  = None

def RestrValueObject:
    '''
    Traces a the value of a variable that is restricted. Can also be used to trace unrestriced variabels, in which case a dummy restriction will be created (doesn't restrict anything).
    '''

    def __init__(self, name, logger, max_restr=None,min_restr=None,init_value=0,signal_list=[1,1,-1]):


        self.tracer = ValueTrace(name)
        logger.add_restriction(self.tracer)

        self.max_restr  = max_restr
        self.init_value = init_value
        self.reset()

        if max_restr == None and min_restr == None:
            self.restriction = DummyRestriction(signal_list)        
        elif max_restr == None and min_restr != None:
            self.restriction = MinRestriction(min_restr,signal_list)        
        elif max_restr != None and min_restr == None:
            self.restriction = MaxRestriction(max_restr,signal_list)
        else:
            self.restriction = MinToMaxRestriction(max_restr,min_restr,signal_list)


    def reset(self):
        self.tracer['cur_value'] = self.init_value

    def set_to_max(self):
        self.tracer['cur_value'] = self.max_restr

    def set_to_min(self):
        self.tracer['cur_value'] = self.min_restr

    def update(self, new_value, restr_signal):
        self.tracer['cur_value']  = new_value
        self.tracer['cur_signal'] = restr_signal

    def update_signal(self, restr_signal):
        self.tracer['cur_signal'] = restr_signal

    def add_value(self, value):
        new_value, restr_signal = self.restriction.add_value(self.cur_value,value)
        self.update(new_value,restr_signal)
        return new_value

    def subtract_value(self, value):
        new_value, restr_signal = self.restriction.subtract_value(self.cur_value,value)
        self.update(new_value,restr_signal)
        return new_value

    def check_max_and_go(self, value):
        new_value, restr_signal = self.restriction.add_value(self.cur_value,value)
        if restr_signal != self.viol_signal:
            self.update(new_value,restr_signal)
            return True
        else:
            self.update_signal(restr_signal)
            return False

    def check_min_and_go(self, value):
        new_value, restr_signal = self.restriction.subtract_value(self.cur_value,value)
        if restr_signal != self.viol_signal:
            self.update(new_value,restr_signal)
            return True
        else:
            self.update_signal(restr_signal)
            return False

