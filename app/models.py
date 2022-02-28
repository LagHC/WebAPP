import datetime as dt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import fields

from app import db, login_manager, ma

class Base(db.Model):
    __abstract__ = True

    def __repr__(self):
        fmt = '{}.{}({})'
        package = self.__class__.__module__
        class_ = self.__class__.__name__
        attrs = sorted(
            (k, getattr(self, k)) for k in self.__mapper__.columns.keys()
        )
        sattrs = ', '.join('{}={!r}'.format(*x) for x in attrs)
        return fmt.format(package, class_, sattrs)

class User(UserMixin, Base):
    """
    Create an User table
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    is_mod = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        """
        Prevent password from being accessed
        """
        raise AttributeError('password is not a readable attribute.')
    
    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Username: {}>'.format(self.username)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class item(Base):

    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    entry_time = db.Column(db.DateTime)
    edit_date = db.Column(db.DateTime)
    edit_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    item_type_id = db.Column(db.Integer, db.ForeignKey('item_type.id'))

    info = db.relationship("item_info", backref="item", cascade="all, delete-orphan", uselist=False)
    images = db.relationship("item_images", backref="item", cascade="all, delete-orphan")


class item_type(Base):

    __tablename__ = 'item_type'

    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship('item', backref = 'item_type', lazy='dynamic')
    name = db.Column(db.String(50), unique=True)
    entry_date = db.Column(db.DateTime)
    edit_date = db.Column(db.DateTime)
    edit_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class item_info(Base):

    __tablename__ = 'item_info'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    Comments = db.Column(db.String(200))
    Price =  db.Column(db.DECIMAL)

    vinyl_info = db.relationship("tblVinyls", backref="item_info_hash", cascade="all, delete-orphan", uselist=False)
    

class tblVinyls(Base):

    __tablename__ = 'vinyl_info'

    id = db.Column(db.Integer, primary_key=True)
    item_info_id = db.Column(db.Integer, db.ForeignKey('item_info.id'))
    Catno = db.Column(db.String(50))
    Artist = db.Column(db.String(50))
    Album = db.Column(db.String(100))
    Sleeve_Grade = db.Column(db.String(20))
    Record_Grade = db.Column(db.String(20))
    Release_Year = db.Column(db.Integer)
    Labels = db.Column(db.String(100))
    Genres = db.Column(db.String(100))
    Styles = db.Column(db.String(100))
    # forSale = db.Column(db.Boolean, nullable=False, default=False)
    wasScanned = db.Column(db.Boolean, nullable=False, default=False)
    needsManualReview = db.Column(db.Boolean, nullable=False, default=False)

class item_images(Base):
    __tablename__ = 'item_images'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    web_path = db.Column(db.String(50), default = '/uploads/images/')
    web_path_thumb = db.Column(db.String(50), default = '/uploads/images/thumbnails/')
    file_name = db.Column(db.String(200))

class BaseSchema(ma.SQLAlchemyAutoSchema):
    entry_date = fields.DateTime(format='%Y-%m-%dT%H:%M:%S%z')
    edit_date = fields.DateTime(format='%Y-%m-%dT%H:%M:%S%z')

class UserSchema(BaseSchema):
    class Meta:
        model = User
        load_instance = True

class ItemTypeSchema(BaseSchema):
    class Meta:
        model = item_type
        include_fk = True
        load_instance = True

class VinylInfoSchema(BaseSchema):
    class Meta:
        model = tblVinyls
        include_fk = True
        load_instance = True

class ItemInfoSchema(BaseSchema):
    class Meta:
        model = item_info
        include_fk = True
        load_instance = True
    vinyl_info = fields.Nested(VinylInfoSchema)

class ItemImageSchema(BaseSchema):
    web_path = fields.Str()
    web_path_thumb = fields.Str()
    file_name = fields.Str()
    # class Meta:
    #     model = item_images
    #     load_instance = True

class ItemSchema(BaseSchema):
    class Meta:
        model = item
        include_fk = True
        load_instance = True
    info = fields.Nested(ItemInfoSchema)
    images = fields.Nested(ItemImageSchema,many=True)
