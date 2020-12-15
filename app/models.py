from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    simp = db.Column(db.String(8))
    trad = db.Column(db.String(8))
    pinyin = db.Column(db.String(32))
    meaning = db.Column(db.String(1024))

    def __repr__(self):
        return f'<Word {self.simplified}'

    def as_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        d['pinyin'] = d['pinyin'][1:-1]
        meaning_string = d['meaning'].strip('/')
        meanings = meaning_string.split('/')
        filtered = list(filter(lambda m: 'CL:' not in m, meanings))
        d['meaning'] = '/'.join(filtered[:3])

        return d


class UserWord(db.Model):
    __tablename__ = 'user_words'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), primary_key=True)
    ammended_meaning = db.Column(db.String(1024))
    bank = db.Column(db.Integer, default=1)
    due_date = db.Column(db.String(12))
    user = db.relationship("User", back_populates='words')
    word = db.relationship("Word")


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    words = db.relationship('UserWord', back_populates="user", 
                            lazy="dynamic", cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)




