import requests
from pprint import pprint
import sqlite3
from datetime import datetime

from teams import Team
from riders import Rider


# create database instance
conn = sqlite3.connect('tour_de_france.db')
cur = conn.cursor()

# import beautiful soup
from bs4 import BeautifulSoup as bs

BASE_URL = "https://www.letour.fr"
riders_page = requests.get("https://www.letour.fr/en/riders")

riders_soup = bs(riders_page.content, 'html.parser')

#
#
# Get the list of teams
#
#
teams = riders_soup.find_all('h3', class_='list__heading')

for team in teams:
    # create table for teams
    cur.execute('''CREATE TABLE IF NOT EXISTS teams (name text, link text)''')
    team_link = BASE_URL + team.find('a')['href']
    team_handle = Team(team.text, team_link)
    
    # check if team is already in database
    if not team_handle.verify_team(cur):
        print(f"Adding {team_handle.name} to database")
        # add team to database
        team_handle.add_to_db(cur)
        conn.commit()


#
#
# Get the list of riders
#
#
team_riders = riders_soup.find_all('div', class_='list__box')

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


#
#
# Get details of each individual Rider
#
#
cur.execute("SELECT * FROM riders")
riders = cur.fetchall()

def get_rider_details(soup):
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

def get_rankings(soup):
    '''
    Get the rankins of each rider like the number of stages won, number of wins, etc.
    '''
    rankings = soup.find('tbody')

    # creating a dictionary to store the rankings
    rider_rankings = []
    # rider_rankings['stage'] = 
    stages = rankings.find_all('tr')

    for stage in stages:
        rider_rankings.append(stage.find_all('td')[1].text.strip())
    return str(rider_rankings)


def get_performance(soup):
    '''
    Get the performance of each rider.
    '''
    performance = soup.find('ul', class_='victory__list')

    perf_list = []
    perf_indicator = performance.find_all('li')

    for indicator in perf_indicator:
        perf_list.append(indicator.find('span', class_='circle').text.strip())
    
    return str(perf_list)
    

for i, rider in enumerate(riders):
    # convert from a tuple to a dictionary
    rider = dict(zip(['bib', 'name', 'team', 'link'], rider))

    print(f"Getting details of {rider['name']}")
    
    # get the rider page
    rider_page = requests.get(rider['link'])
    rider_soup = bs(rider_page.content, 'html.parser')

    # get the rider's image, country, birth date and age
    rider_image, rider_country, rider_birth, rider_age = get_rider_details(rider_soup)

    # get stage rankins details
    rider_rankings = get_rankings(rider_soup)

    # get performance details
    rider_performance = get_performance(rider_soup)


    # add the rider's image, country, birth date and age to the database
    if i < 1:
        cur.execute("ALTER TABLE riders ADD COLUMN image text")
        cur.execute("ALTER TABLE riders ADD COLUMN country text")
        cur.execute("ALTER TABLE riders ADD COLUMN birth text")
        cur.execute("ALTER TABLE riders ADD COLUMN age text")
        cur.execute("ALTER TABLE riders ADD COLUMN rankings text")
        cur.execute("ALTER TABLE riders ADD COLUMN performance text")
    
    cur.execute("UPDATE riders SET image = ?, country = ?, birth = ?, age = ?, rankings = ?, performance = ? WHERE bib = ?", (rider_image, 
                                                                                                                              rider_country, 
                                                                                                                              rider_birth, 
                                                                                                                              rider_age, 
                                                                                                                              rider_rankings, 
                                                                                                                              rider_performance, 
                                                                                                                              rider['bib']))
    conn.commit()

