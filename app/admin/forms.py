from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, InputRequired, Optional, Length, AnyOf
from flask_wtf.file import FileAllowed
import re

class ItemTypeForm(FlaskForm):
    """
    Form for admin to add or edit an itemtype
    """
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class VinylForm(FlaskForm):
    """
    Form for admin to add or edit vinyls
    """
    Catno = StringField('Catno', validators=[DataRequired(), Length(max=50)])
    Artist = StringField('Artist', validators=[DataRequired(), Length(max=50)])
    Album = StringField('Album', validators=[Length(max=100)])
    Sleeve_Grade = SelectField('Sleeve Grade', choices =[('Fair (F)'),('Good (G)'),('Good + (G+)'),('Very Good (VG)'),('Very Good + (VG+)'),('Near Mint (NM)'),('Mint/Sealed (M)')], validators=[AnyOf([('Fair (F)'),('Good (G)'),('Good + (G+)'),('Very Good (VG)'),('Very Good + (VG+)'),('Near Mint (NM)'),('Mint/Sealed (M)')])])
    Record_Grade = SelectField('Record Grade', choices =[('Fair (F)'),('Good (G)'),('Good + (G+)'),('Very Good (VG)'),('Very Good + (VG+)'),('Near Mint (NM)'),('Mint/Sealed (M)')], validators=[AnyOf([('Fair (F)'),('Good (G)'),('Good + (G+)'),('Very Good (VG)'),('Very Good + (VG+)'),('Near Mint (NM)'),('Mint/Sealed (M)')])])
    Comments = StringField('Comments', validators=[Length(max=200)])
    Price = DecimalField('Price',validators=[Optional(strip_whitespace=True)])
    Pictures = MultipleFileField('Images', validators=[FileAllowed(['jpg','png'], 'Images Only')])
    submit = SubmitField('Submit')

    def validate_image(form, field):
        if field.data:
            field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)