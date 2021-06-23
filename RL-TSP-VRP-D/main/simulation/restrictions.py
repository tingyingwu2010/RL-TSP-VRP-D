'''

'''
import numpy as np
from main.simulation.common_sim_func import param_interpret

def is_None(value):
    return np.isnan(value) or value == None or value == np.nan


def is_not_None(value):
    return not is_None(value)



class MinToMaxRestriction:
    '''
    Used for standard restrictions.The signal list follows this order:
    - If no restriction is violated, its called non violation (non_viol_signal = signal_list[0])
    - If the restriction is violated, but the changed amount is greater than zero its a semi violation (semi_viol_signal = signal_list[1])
    - A restriction violation resulting in a changed amount of zero will be interpreted as a full violation (viol_signal = signal_list[2])
    The violation signal can be used to calculate a reward or penalization.
    '''
    def __init__(self, max_restr, min_restr):
        self.max_restr = max_restr
        self.min_restr = min_restr


    def add_value(self, cur_value, value):
        '''
        Adds a specified amount to the current value under the initialzied max restriction.
        '''
        if is_None(cur_value):
            return value, 0

        new_value = cur_value + value
        
        if new_value <= self.max_restr:
            cur_value = new_value
            # return 1 to signal NO violation
            return cur_value, 0
        elif cur_value == self.max_restr:
            # return -1 to signal violation
            return cur_value, 2
        else:
            return cur_value, 1


    def subtract_value(self, cur_value, value):
        '''
        Subtracts a specified amount from the current value under the initialzied min restriction.
        '''
        if is_None(cur_value):
            return value, 0

        new_value = cur_value - value
        
        if new_value >= self.min_restr:
            cur_value = new_value
            # return 1 to signal NO violation
            return cur_value, 0
        elif cur_value == self.min_restr:
            # return -1 to signal violation
            return cur_value, 2
        else:
            return cur_value, 1


class MinRestriction(MinToMaxRestriction):
    '''
    Extension for MinToMaxRestriction class, that excludes the max restriction.
    '''
    def __init__(self, min_restr):
        super().__init__(None, min_restr)

    def add_value(self, cur_value, value):
        '''
        Overrides the max restriction from the original class to unrestricted max.
        '''
        if is_None(cur_value):
            return value, 0
        return cur_value + value, 0


class MaxRestriction(MinToMaxRestriction):
    '''
    Extension for MinToMaxRestriction class, that excludes the min restriction.
    '''
    def __init__(self, max_restr):
        super().__init__(max_restr, None,)

    def subtract_value(self, cur_value, value):
        '''
        Overrides the min restriction from the original class to unrestricted min.
        '''
        if is_None(cur_value):
            return value, 0
        return cur_value - value, 0


class DummyRestriction(MinToMaxRestriction):
    '''
    Used when no restrictions are needed. Extension for MinToMaxRestriction class, that excludes both the min and the max restriction
    '''
    def __init__(self):
        super().__init__(None, None)

    def add_value(self, cur_value, value):
        '''
        Overrides the max restriction from the original class to unrestricted max.
        '''
        if is_None(cur_value):
            return value, 0
        return cur_value + value, 0

    def subtract_value(self, cur_value, value):
        '''
        Overrides the min restriction from the original class to unrestricted min.
        '''
        if is_None(cur_value):
            return value, 0
        return cur_value - value, 0


class RestrValueObject:
    '''
    Traces a the value of a variable that is restricted. Can also be used to trace unrestriced variabels, in which case a dummy restriction will be created (doesn't restrict anything).
    '''

    def __init__(self, name, obj_index, index_type, temp_db, max_restr=None, min_restr=None, init_value=None, rate=None):

        #'range', v_index, 'vehicle', temp_db, v_params['max_range'], 0, v_params['max_range'], v_params['speed']
        #'n_items', n_index, 'node', temp_db, n_params['max_items'], 0, n_params['init_items']
        self.name = name
        self.obj_index = obj_index
        self.temp_db = temp_db

        self.max_restr  = param_interpret(max_restr)
        self.min_restr  = param_interpret(min_restr)

        if init_value == np.nan or init_value == 'max':
            self.init_value = self.max_restr
        elif init_value == 'min':
            self.init_value = self.min_restr
        else:
            self.init_value = param_interpret(init_value)
        
        self.rate = param_interpret(rate)

        if max_restr == None and min_restr == None:
            self.restriction = DummyRestriction()        
        elif max_restr == None and min_restr != None:
            self.restriction = MinRestriction(min_restr)        
        elif max_restr != None and min_restr == None:
            self.restriction = MaxRestriction(max_restr)
        else:
            self.restriction = MinToMaxRestriction(max_restr,min_restr)

        self.temp_db.add_restriction(self, name, obj_index, index_type)
        self.temp_db.prep_max_min(name, max_restr, min_restr, rate)

        self.reset()
        self.reset_signal()


    def calc_time(self, value):
        if self.rate is not None:
            return self.rate*value
        return 0


    def in_time(self):
        if self.rate is not None:
            if is_not_None(self.temp_db.cur_time_frame):
                self.temp_db.status_dict['in_time_'+self.name][self.obj_index] = self.rate*self.temp_db.cur_time_frame
            else:
                self.temp_db.status_dict['in_time_'+self.name][self.obj_index] = 0
        else:
            self.temp_db.status_dict['in_time_'+self.name][self.obj_index] = np.nan

    def cur_value(self, none_to_val=None):
        if is_None(self.temp_db.status_dict[self.name][self.obj_index]):
            return none_to_val
        return self.temp_db.status_dict[self.name][self.obj_index]

    def reset(self):
        self.temp_db.status_dict[self.name][self.obj_index] = self.init_value

    def reset_signal(self):
        self.temp_db.signals_dict['signal_'+self.name][self.obj_index] = 0

    def set_to_max(self):
        self.temp_db.status_dict[self.name][self.obj_index] = self.max_restr

    def set_to_min(self):
        self.temp_db.status_dict[self.name][self.obj_index] = self.min_restr


    def update(self, new_value, restr_signal):
        if self.rate is not None:
            if is_not_None(self.temp_db.status_dict[self.name][self.obj_index]):
                self.temp_db.status_dict['in_time_'+self.name][self.obj_index] = (
                    self.temp_db.status_dict['in_time_'+self.name][self.obj_index] - abs(
                        abs(self.temp_db.status_dict[self.name][self.obj_index]) - abs(new_value)
                    )
                )
            else:
                self.temp_db.status_dict['in_time_'+self.name][self.obj_index] = max(
                    self.temp_db.status_dict['in_time_'+self.name][self.obj_index] - abs(new_value), 0
                )

        if is_not_None(self.temp_db.status_dict[self.name][self.obj_index]):
            self.temp_db.status_dict[self.name][self.obj_index] = new_value

        self.temp_db.signals_dict['signal_'+self.name][self.obj_index] = self.temp_db.signal_list[restr_signal]

    def update_signal(self, restr_signal):
        self.temp_db.signals_dict['signal_'+self.name][self.obj_index] = self.temp_db.signal_list[restr_signal]


    def add_value(self, value):
        if is_not_None(self.temp_db.status_dict['in_time_'+self.name][self.obj_index]):
            value = min(value, self.temp_db.status_dict['in_time_'+self.name][self.obj_index])
        
        new_value, restr_signal = self.restriction.add_value(self.temp_db.status_dict[self.name][self.obj_index], value)
        self.update(new_value,restr_signal)
        
        return new_value

    def subtract_value(self, value):
        if is_not_None(self.temp_db.status_dict['in_time_'+self.name][self.obj_index]):
            value = min(value, self.temp_db.status_dict['in_time_'+self.name][self.obj_index])
        
        new_value, restr_signal = self.restriction.subtract_value(self.temp_db.status_dict[self.name][self.obj_index], value)
        self.update(new_value,restr_signal)
        return new_value


    def check_add_value(self, value, in_time=True):
        if value is None:
            value = self.max_restr - self.cur_value(none_to_val=0)
        
        if is_not_None(self.temp_db.status_dict['in_time_'+self.name][self.obj_index]) and in_time:
            value = min(value, self.temp_db.status_dict['in_time_'+self.name][self.obj_index])
        
        new_value, restr_signal = self.restriction.add_value(self.temp_db.status_dict[self.name][self.obj_index], value)
        
        if is_None(self.temp_db.status_dict[self.name][self.obj_index]):
            return new_value
        return new_value - self.temp_db.status_dict[self.name][self.obj_index]

    def check_subtract_value(self, value, in_time=True):
        if value is None:
            value = self.cur_value(none_to_val=self.max_restr)

        if is_not_None(self.temp_db.status_dict['in_time_'+self.name][self.obj_index]) and in_time:
            value = min(value, self.temp_db.status_dict['in_time_'+self.name][self.obj_index])
        
        new_value, restr_signal = self.restriction.subtract_value(self.temp_db.status_dict[self.name][self.obj_index], value)
        
        if is_None(self.temp_db.status_dict[self.name][self.obj_index]):
            return new_value
        return self.temp_db.status_dict[self.name][self.obj_index] - new_value

