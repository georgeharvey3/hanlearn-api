import re
import unidecode
from datetime import datetime, timedelta

def process_word_row(db_row, due_date=None):
    meanings = db_row['meaning'].split('/')
    meanings = [meaning for meaning in meanings[:3] if meaning]
    cleanings = []
    for meaning in meanings[:3]:
        if meaning:
            if re.findall(r'[\u4e00-\u9fff]+', meaning):
                continue
            if "(" in meaning:
                meaning = re.sub(r'\([^)]*\)', '', meaning)
                meaning = meaning.strip()
            if len(meaning) < 20: 
                if meaning.startswith('to '):
                    meaning = meaning.replace('to ', '')
                if meaning.startswith('the '):
                    meaning = meaning.replace('the ', '')
                cleanings.append(unidecode.unidecode(meaning))
    if len(cleanings) == 0:
        cleanings.append('---')
    cleanings = '/'.join(cleanings)
    pinyin = db_row['pinyin'].lstrip('[')
    pinyin = pinyin.rstrip(']')

    word_dict = {'simp': db_row['simp'], 'trad': db_row['trad'],
                    'id': db_row['id'], 'meaning': cleanings,
                    'pinyin': pinyin, 'due_date': due_date}
    return word_dict

def process_clash_row(db_row):
    meanings = db_row['meaning'].split('/')
    meanings = [meaning for meaning in meanings[:3] if meaning]
    for meaning in meanings[:3]:
        if meaning:
            if re.findall(r'[\u4e00-\u9fff]+', meaning):
                continue
    meaning = meanings[0]
    pinyin = db_row['pinyin'][1:-1]
    word_dict = {'simp': db_row['simp'], 'trad': db_row['trad'],
                'id': db_row['id'], 'meaning': meaning,
                'pinyin': pinyin}
    return word_dict

def new_due_date(bank):
    intervals = {
        1: 1,
        2: 3,
        3: 7,
        4: 30,
        5: 60
    }

    new_date = (datetime.utcnow() + timedelta(days=intervals[bank])).date()

    return new_date.strftime("%Y/%m/%d")

def overdue_by(date):
    date_obj = datetime.strptime(date, "%Y/%m/%d")
    return (datetime.utcnow() - date_obj).days
