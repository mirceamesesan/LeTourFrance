from dataclasses import dataclass

@dataclass
class Team:
    '''
    Team class that holds the team name and the team members    
    '''
    name: str
    link: str

    def add_to_db(self, c):
        '''Add the team to the database'''
        c.execute("INSERT INTO teams VALUES (?, ?)", (self.name, self.link))


    def verify_team(self, c):
        '''Check if the team is already in the database'''
        c.execute("SELECT * FROM teams WHERE name = ?", (self.name,))
        return c.fetchone() is not None
    
