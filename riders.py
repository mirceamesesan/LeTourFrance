from dataclasses import dataclass

@dataclass
class Rider:
    '''
    Contains all useful information about a rider
    '''
    bib: int
    name: str
    team: str
    link: str
    

    def add_to_db(self, c):
        '''Add the rider to the database'''
        c.execute("INSERT INTO riders VALUES (?, ?, ?, ?)", (self.bib, 
                                                             self.name, 
                                                             self.team, 
                                                             self.link))


    def verify_rider(self, c):
        '''Check if the rider is already in the database'''
        c.execute("SELECT * FROM riders WHERE bib = ?", (self.bib,))
        return c.fetchone() is not None