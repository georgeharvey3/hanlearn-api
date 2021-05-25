from flask import Blueprint, jsonify, request, make_response
from . import main
from .. import db
from ..models import Word, User, UserWord
from ..helpers import new_due_date, overdue_by, process_word_row
from ..decorators import token_required
from datetime import datetime, timedelta, date
import random
from google_trans_new import google_translator

@main.route('/api/add-word', methods=['POST'])
def add_word():
    word = request.get_json(force=True)

    u = User.query.all()[0]

    w = Word.query.filter_by(id=word['id']).first()

    uw = UserWord(user=u, word=w)

    if len(UserWord.query.all()) > 9:
        date_obj = datetime.utcnow() + timedelta(days=1)
    else:
        date_obj = datetime.utcnow()
        print(date_obj)

    uw.due_date = date_obj.strftime("%Y/%m/%d")

    db.session.add(uw)
    db.session.commit()

    res = make_response(jsonify({"message": "OK"}), 201)

    return res

@main.route('/api/remove-word', methods=['POST'])
def remove_word():
    word_id = request.get_json(force=True)

    u = User.query.all()[0]

    uw = u.words.filter_by(word_id=word_id).first()
    if uw:
        db.session.delete(uw)

    db.session.commit()

    res = make_response(jsonify({"message": "OK"}), 201)

    return res

@main.route('/api/get-word/<character>/<char_set>')
def get_word(character, char_set):

    word_list = Word.query.filter(getattr(Word, char_set) == character).all()

    word_dicts = [process_word_row(word.as_dict()) for word in word_list]

    res = make_response(jsonify({"words": word_dicts}), 200)

    return res

@main.route('/api/get-user-words')
@token_required
def get_user_words(current_user):

    user_word_entries = UserWord.query.filter_by(user_id=current_user.id).all()
    user_words_sorted = sorted(user_word_entries, key=lambda x: x.due_date)
    ammended_dict = {uw.word_id: uw.ammended_meaning for uw in user_words_sorted}
    words = [process_word_row(user_word.word.as_dict(), user_word.due_date, user_word.bank) for user_word in user_words_sorted]

    for word in words:
        if ammended_dict[word['id']]:
            word['meaning'] = ammended_dict[word['id']]

    res = make_response(jsonify({'words': words}), 200)
    
    return res

@main.route('/api/get-due-user-words')
@token_required
def get_due_user_words(current_user):

    user_words = UserWord.query.filter_by(user_id=current_user.id).all()
    due_user_words = list(filter(lambda x: overdue_by(x.due_date) >= 0, user_words))
    ammended_dict = {uw.word_id: uw.ammended_meaning for uw in due_user_words}
    words = [word.word.as_dict() for word in due_user_words]

    for word in words:
        if ammended_dict[word['id']]:
            word['meaning'] = ammended_dict[word['id']]

    res = make_response(jsonify({'words': words}), 200)
    
    return res

@main.route('/api/update-word-meaning', methods=['POST'])
@token_required
def update_word_meaning(current_user):
    word_data = request.get_json(force=True)

    user_word_obj = UserWord.query.filter_by(user_id=current_user.id).filter_by(word_id=word_data['word_id']).first()
    user_word_obj.ammended_meaning = word_data['new_meaning']
    db.session.add(user_word_obj)
    db.session.commit()

    res = make_response(jsonify({"message": "OK"}), 201)
    return res

@main.route('/api/finish-test', methods=['POST'])
@token_required
def finish_test(current_user):
    req = request.get_json()
    current_user_words = current_user.words
    for word in req['scores']:
        w = current_user_words.filter_by(word_id=word['word_id']).first()

        if word['score'] == 4 and w.bank < 5:
            w.bank += 1
        if word['score'] < 4:
            w.bank = 1
        
        w.due_date = new_due_date(w.bank)
        db.session.add(w)
        db.session.commit()
    
    res = make_response(jsonify({"message": "OK"}), 201)

    return res

@main.route('/api/translate-sentence', methods=['POST'])
def tranlate_sentence():
    req = request.get_json()
    sentence = req['sentence']
    translator = google_translator()
    translated = translator.translate(sentence, lang_tgt='en')

    res = make_response(jsonify({'translated': translated}))

    return res

@main.route('/api/get-chengyu')
def get_chengyu():
    file = "./app/chengyus.txt"

    with open(file) as f:
        chengyus = f.readlines()

    base_date = date(2021, 5, 24)
    today = datetime.utcnow().date()
    index = (today - base_date).days % len(chengyus)
    chengyu = chengyus.pop(index)

    options = random.sample(chengyus, 3)
    
    options.append(chengyu)

    chengyu_chinese = chengyu.split('/')[0]
    correct = chengyu.split('/')[-1]
    meaning_options = [m.split('/')[-1] for m in options]

    random.shuffle(meaning_options)

    char_results = []

    for c in chengyu_chinese:
        trads = []
        pinyins = []
        meanings = []

        words = Word.query.filter_by(simp=c).all()

        for w in words:
            trads.append(w.trad)
            pinyins.append(w.pinyin[1:-1])
            meanings.extend(w.meaning.split("/"))
        
        result = {
            'char': c,
            'trads': [t for t in set(trads) if t][:10],
            'pinyins': [p for p in set(pinyins) if p][:10],
            'meanings': [m for m in set(meanings) if m][:10]
        }

        char_results.append(result)

    res = {
        'chengyu': chengyu_chinese, 
        'options': meaning_options,
        'correct': correct,
        'char_results': char_results
        }
    
        
    return res

@main.route('/api/lookup-chengyu-char/<char>')
def lookup_chengyu_char(char):

    trads = []
    pinyins = []
    meanings = []

    words = Word.query.filter_by(simp=char).all()

    for w in words:
        trads.append(w.trad)
        pinyins.append(w.pinyin[1:-1])
        meanings.extend(w.meaning.split("/"))
    
    res = make_response(jsonify({
        'trads': trads,
        'pinyins': pinyins,
        'meanings': meanings
    }))

    return res

    
    


