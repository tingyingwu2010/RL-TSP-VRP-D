


class BaseAutoAgent:

    def __init__(self, temp_db):

        self.temp_db = temp_db


    def find_destination(self):
        
        if self.temp_db.base_groups['vehicles'][self.temp_db.cur_v_index].items.cur_value() > 0 and 0 in self.temps_db.customers(self.temp_db.status_dict['c_waiting']):
            n_index = self.find_customer()
            self.temp_db.status_dict['c_waiting'][n_index] = 1            

        else:
            n_index = self.find_depot()

        if n_index is None:
            return None

        return self.temp_db.status_dict['c_coord'][n_index]


    def find_v_to_unload(self):
        
        if any(self.temp_db.v_transporting_v[self.temp_db.cur_v_index]):
            return self.temp_db.v_transporting_v[self.temp_db.cur_v_index][0]
        return None
    

    def find_v_to_load(self):

        return self.temp_db.nearest_neighbour(self.temps_db.vehicles(
            self.temp_db.status_dict['v_coord'],
            include=[[self.temp_db.status_dict['v_loadable'], 1], [self.temp_db.status_dict['v_free'], 1]]
            )
        )
    

    def find_customer(self):
        return self.temp_db.nearest_neighbour(self.temps_db.customers(
            self.temp_db.status_dict['n_coord'],
            include=[[self.temp_db.status_dict['c_waiting'], 0]],
            exclude=[[self.temp_db.status_dict['n_items'], 0]]
            )
        )
    

    def find_depot(self):
        return self.temp_db.nearest_neighbour(self.temps_db.depots(
            self.temp_db.status_dict['n_coord'],
            exclude=[[self.temp_db.status_dict['n_items'], 0]]
            )
        ) 

