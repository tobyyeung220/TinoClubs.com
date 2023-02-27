# PUT THIS IN main.py

import json
import os
from db import Club


def keep_only_ascii(text: str) -> str:
    return ''.join(char for char in text if char.isalpha() or char == ' ').strip()


def load_club_officers(club_leadership_text):
    acceptable_roles = ['president', 'vice', 'vp', 'secretary', 'treasurer']
    return [{'name': keep_only_ascii(line.split(',')[0]), 'role': line.split(',')[2].strip()} for line in club_leadership.split('\n') if len(line.split(',')) >= 3 and any(r in line.split(',')[2].strip().lower() for r in acceptable_roles)]


for club_data_json in os.listdir('JSONs'):
    club_data = json.load(open(os.path.join('JSONs', club_data_json), 'r'))
    club_leadership = club_data['officers']
    print()
    # print('-' * 100)
    print(club_data['name'])
    print(club_leadership)
    officer_info = load_club_officers(club_leadership)
    print(officer_info)
    if (record := input('y to ok or enter custom data: ')) != 'y':
        while 1:
            try:
                officer_info = json.loads(record)
                break
            except:
                record = input('invalid json, try again: ')
    with open('test.txt', 'a') as file:
        file.write(club_data['name'] + ' ' + json.dumps(officer_info) + '\n')
