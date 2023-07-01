import requests
from pprint import pprint
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup as bs

from teams import Team
from riders import Rider
from stages import Stage


# create database instance
conn = sqlite3.connect('tour_de_france.db')
cur = conn.cursor()

BASE_URL = "https://www.letour.fr"
riders_page = requests.get("https://www.letour.fr/en/riders")
stages_page = requests.get("https://www.letour.fr/en/overall-route")

def main():
    riders_soup = bs(riders_page.content, 'html.parser')
    stages_soup = bs(stages_page.content, 'html.parser')
    
    get_list_of_teams(riders_soup)
    get_list_of_riders(riders_soup)
    get_details_of_riders()
    get_list_of_stages(stages_soup)


def get_list_of_stages(soup):
    '''
    Get the list of stages
    '''
    stages_table = soup.find('tbody')
    stages = stages_table.find_all('tr')
    # create table for stages
    cur.execute('''CREATE TABLE IF NOT EXISTS stages (stage_number text, 
                                                      type text,
                                                      date text,
                                                      start_finish text,
                                                      distance text,
                                                      link text)''')

    for stage in stages:
        stage_number = stage.find_all('td')[0].text.strip()
        stage_type = stage.find_all('td')[1].text.strip()
        stage_date = stage.find_all('td')[2].text.strip()
        stage_start_finish = stage.find_all('td')[3].text.strip()
        stage_distance = stage.find_all('td')[4].text.strip()
        stage_link = BASE_URL + stage.find_all('td')[5].find('a')['href']

        stage_handle = Stage(stage_number, 
                             stage_type, 
                             stage_date, 
                             stage_start_finish, 
                             stage_distance, 
                             stage_link)
        
        # check if stage is already in database
        if not stage_handle.verify_stage(cur):
            print(f"Adding stage {stage_handle.stage_number} to database")
            # add stage to database
            stage_handle.add_to_database(cur)
            conn.commit()


def get_list_of_teams(soup):
    '''
    Get the list of teams
    '''
    teams = soup.find_all('h3', class_='list__heading')
    # create table for teams
    cur.execute('''CREATE TABLE IF NOT EXISTS teams (name text, link text)''')

    for team in teams:
        team_link = BASE_URL + team.find('a')['href']
        team_handle = Team(team.text, team_link)
        
        # check if team is already in database
        if not team_handle.verify_team(cur):
            print(f"Adding {team_handle.name} to database")
            # add team to database
            team_handle.add_to_db(cur)
            conn.commit()


def get_list_of_riders(soup):
    '''Get the list of riders for each team'''''
    team_riders = soup.find_all('div', class_='list__box')

    for riders in team_riders:
        # get above div element with class list__heading
        team_name = riders.find_previous_sibling('h3', class_='list__heading').text

        for rider in riders.find_all('li'):
            rider_bib = rider.find('span', class_='bib').text
            rider_name = rider.find('span', class_='runner').text.strip()
            rider_link = BASE_URL + rider.find('a')['href']
            rider_team = team_name

            # create table for riders
            cur.execute('''CREATE TABLE IF NOT EXISTS riders (bib int, name text, team text, link text)''')
            runner = Rider(rider_bib, rider_name, rider_team, rider_link)

            # check if rider is already in database
            if not runner.verify_rider(cur):
                print(f"Adding {runner.name} to database")
                # add rider to database
                runner.add_to_db(cur)
                conn.commit()


def run_rider_details(soup):
    '''
    Get the details of each rider
    '''
    rider_header = soup.find('div', class_='pageHeader')

    # get image link
    rider_image = rider_header.find('img')['data-src']
    rider_country = rider_header.find('span', class_='riderInfos__country__name').text.strip()
    _birth = rider_header.find('span', class_='riderInfos__birth').text.strip(" born on \n")
    rider_birth = datetime.strptime(_birth, '%d/%m/%Y').date()
    # get the rider's age
    rider_age = datetime.now().year - rider_birth.year - ((datetime.now().month, datetime.now().day) < (rider_birth.month, rider_birth.day))

    return rider_image, rider_country, rider_birth, rider_age


def run_rider_rankings(soup):
    '''
    Get the rankins of each rider like the number of stages won, number of wins, etc.
    '''
    rankings = soup.find('tbody')

    # creating a dictionary to store the rankings
    rider_rankings = []
    stages = rankings.find_all('tr')

    for stage in stages:
        rider_rankings.append(stage.find_all('td')[1].text.strip())

    return str(rider_rankings)


def run_rider_performance(soup):
    '''
    Get the performance of each rider.
    '''
    performance = soup.find('ul', class_='victory__list')

    perf_list = []
    perf_indicator = performance.find_all('li')

    for indicator in perf_indicator:
        perf_list.append(indicator.find('span', class_='circle').text.strip())
    
    return str(perf_list)
    

def get_details_of_riders():
    '''Get details of each individual Rider'''
    cur.execute("SELECT * FROM riders")
    riders = cur.fetchall()

    for i, rider in enumerate(riders):
        # convert from a tuple to a dictionary
        rider = dict(zip(['bib', 'name', 'team', 'link'], rider))
        print(f"Getting details of {rider['name']}")
        
        # get the rider page
        rider_page = requests.get(rider['link'])
        rider_soup = bs(rider_page.content, 'html.parser')

        # get the rider's image, country, birth date and age
        rider_image, rider_country, rider_birth, rider_age = run_rider_details(rider_soup)

        # get stage rankins details
        rider_rankings = run_rider_rankings(rider_soup)

        # get performance details
        rider_performance = run_rider_performance(rider_soup)


        # add the rider's image, country, birth date and age to the database
        # if i < 1:
        #     cur.execute("ALTER TABLE riders ADD COLUMN image text")
        #     cur.execute("ALTER TABLE riders ADD COLUMN country text")
        #     cur.execute("ALTER TABLE riders ADD COLUMN birth text")
        #     cur.execute("ALTER TABLE riders ADD COLUMN age text")
        #     cur.execute("ALTER TABLE riders ADD COLUMN rankings text")
        #     cur.execute("ALTER TABLE riders ADD COLUMN performance text")
        
        cur.execute("UPDATE riders SET image = ?, country = ?, birth = ?, age = ?, rankings = ?, performance = ? WHERE bib = ?", (rider_image, 
                                                                                                                                rider_country, 
                                                                                                                                rider_birth, 
                                                                                                                                rider_age, 
                                                                                                                                rider_rankings, 
                                                                                                                                rider_performance, 
                                                                                                                                rider['bib']))
        conn.commit()


if __name__ == "__main__":
    main()
    conn.close()