from flask import Blueprint, jsonify, request, make_response
from . import main
from .. import db
from ..models import Word, User, UserWord
from ..helpers import new_due_date, overdue_by, process_word_row
from ..decorators import token_required


@main.route('/add-word', methods=['POST'])
def add_word():
    word = request.get_json(force=True)

    u = User.query.all()[0]

    w = Word.query.filter_by(id=word['id']).first()

    uw = UserWord(user=u, word=w)

    db.session.add(uw)
    db.session.commit()

    res = make_response(jsonify({"message": "OK"}), 201)

    return res

@main.route('/remove-word', methods=['POST'])
def remove_word():
    word_id = request.get_json(force=True)

    u = User.query.all()[0]

    uw = u.words.filter_by(word_id=word_id).first()
    if uw:
        db.session.delete(uw)

    db.session.commit()

    res = make_response(jsonify({"message": "OK"}), 201)

    return res

@main.route('/get-word/<character>/<char_set>')
def get_word(character, char_set):

    word_list = Word.query.filter(getattr(Word, char_set) == character).all()

    word_dicts = [process_word_row(word.as_dict()) for word in word_list]

    res = make_response(jsonify({"words": word_dicts}), 200)

    return res

@main.route('/get-user-words')
@token_required
def get_user_words(current_user):

    user_word_entries = UserWord.query.filter_by(user_id=current_user.id).all()
    user_words_sorted = sorted(user_word_entries, key=lambda x: x.due_date)
    ammended_dict = {uw.word_id: uw.ammended_meaning for uw in user_words_sorted}
    words = [process_word_row(user_word.word.as_dict(), user_word.due_date) for user_word in user_words_sorted]

    for word in words:
        if ammended_dict[word['id']]:
            word['meaning'] = ammended_dict[word['id']]

    res = make_response(jsonify({'words': words}), 200)
    
    return res

@main.route('/get-due-user-words')
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

@main.route('/update-word-meaning', methods=['POST'])
@token_required
def update_word_meaning(current_user):
    word_data = request.get_json(force=True)

    user_word_obj = UserWord.query.filter_by(user_id=current_user.id).filter_by(word_id=word_data['word_id']).first()
    user_word_obj.ammended_meaning = word_data['new_meaning']
    db.session.add(user_word_obj)
    db.session.commit()

    res = make_response(jsonify({"message": "OK"}), 201)
    return res

@main.route('/finish-test', methods=['POST'])
@token_required
def finish_test(current_user):
    req = request.get_json()
    current_user_words = current_user.words
    for word in req['scores']:
        w = current_user_words.filter_by(word_id=word['word_id']).first()
        if word['score'] == 4:
            if w.bank < 5:
                w.bank += 1
                w.due_date = new_due_date(w.bank)
                db.session.add(w)
                db.session.commit()
            else:
                UserWord.query.filter_by(word_id=word['word_id']).delete()
        if word['score'] < 3:
            if w.bank > 1:
                w.bank -= 1
                w.due_date = new_due_date(w.bank)
                db.session.add(w)
                db.session.commit()
    
    res = make_response(jsonify({"message": "OK"}), 201)

    return res
