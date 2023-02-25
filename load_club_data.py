# PUTS THIS IN main.py

import json
import os
from db import Club

categories_mapping = {
    'volunteering & honor societies': ClubCategory.volunteering,
    'hobbies & interest': ClubCategory.hobbies,
    'culture & ethnicities': ClubCategory.culture_and_identity,
    'other': ClubCategory.culture_and_identity,
    'sports & athletics': ClubCategory.sports,
    'stem & tech': ClubCategory.stem,
    'business & politics': ClubCategory.business,
    'culture (or activist society)': ClubCategory.culture_and_identity,
    'volunteering&honor societies': ClubCategory.hobbies,
    'volunteering/service club': ClubCategory.volunteering,
    'stem & tech, student publication': ClubCategory.stem,
    'interest club': ClubCategory.hobbies,
    'other (activist society)': ClubCategory.culture_and_identity
}

for file in os.listdir("JSONs"):
    club_data = json.load(open(os.path.join("JSONs", file), 'r'))
    category = club_data['category'].replace('and', '&').replace('interests', 'interest')
    with app.app_context():
        try:
            Club.create(name=club_data['name'], aka='', category=categories_mapping[category], description='',
                        meeting_time=club_data['meeting_time'], meeting_location=club_data['advisor_room'], raw_tags='',
                        raw_social_medias=json.dumps(
                            [{'name': 'email', 'url': 'mailto:' + club_data['email'], 'text': club_data['email']}]),
                        raw_leaderships=json.dumps([{'name': club_data['advisor_name'], 'role': 'Advisor'}]),
                        is_new=False)
        except Exception as e:
            print(e, club_data)
