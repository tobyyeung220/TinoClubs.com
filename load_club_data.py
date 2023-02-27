# PUT THIS IN main.py

def minDistance(word1, word2):
    m = len(word1)
    n = len(word2)
    table = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        table[i][0] = i
    for j in range(n + 1):
        table[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                table[i][j] = table[i - 1][j - 1]
            else:
                table[i][j] = 1 + min(table[i - 1][j], table[i][j - 1], table[i - 1][j - 1])
    return table[-1][-1]


import json
from db import Club

with app.app_context():
    all_club_names = [row[0] for row in Club.query.with_entities(Club.name).all()]

for line in open('test.txt', 'r'):
    bracket_idx = line.index('[')
    wrong_club_name, leadership_list = line[:bracket_idx - 1], line[bracket_idx:]
    if wrong_club_name == 'Cupertino ASL Club':
        wrong_club_name = 'ASL'
    elif wrong_club_name == 'Tino Explore (STEAM Magazine) Club':
        wrong_club_name = 'Tino Explore'
    elif wrong_club_name == 'Cupertino Bullet Journal Club':
        wrong_club_name = 'Bullet Journay Calliography Club'
    with app.app_context():
        acronyms_matchiin_clubs = Club.query.filter(Club.aka.like(f'%{wrong_club_name}%')).all()
    if wrong_club_name == 'Interact':
        actual_club_name = 'Cupertino Interact'
    elif acronyms_matchiin_clubs:
        actual_club_name = acronyms_matchiin_clubs[0].name
    else:
        actual_club_name = sorted(all_club_names, key=lambda n: minDistance(n, wrong_club_name))[0]
    # print(actual_club_name, json.loads(leadership_list))
    with app.app_context():
        existing_club = db.get_or_404(Club, actual_club_name)
        existing_leadership = json.loads(existing_club.leaderships_in_json)
        print(actual_club_name, existing_leadership)
        # existing_club.leaderships_in_json = json.dumps(existing_leadership + json.loads(leadership_list))
        # db.session.commit()
        # print(existing_club, wrong_club_name)
exit()