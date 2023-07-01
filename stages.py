from dataclasses import dataclass

@dataclass
class Stage:
    '''
    Storing all the general information about the stages
    '''
    stage_number: str
    stage_type: str
    stage_date: str
    stage_start_finish: str
    stage_distance: str
    stage_link: str

    def add_to_database(self, c):
        '''
        Add the stage details to the database
        '''
        c.execute("INSERT INTO stages VALUES (?, ?, ?, ?, ?, ?)", 
                    (self.stage_number, 
                     self.stage_type, 
                     self.stage_date, 
                     self.stage_start_finish,
                     self.stage_distance, 
                     self.stage_link))
        
    def verify_stage(self, c):
        '''
        Check if the stage is already in the database
        '''
        c.execute("SELECT * FROM stages WHERE date = ?", (self.stage_date,))
        return c.fetchone() is not None
