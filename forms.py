from flask_wtf import FlaskForm
from wtforms import FileField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired

class ImageForm(FlaskForm):
    image = FileField('Upload Image', validators=[DataRequired()])
    stripe_width = IntegerField('Stripe Width', validators=[DataRequired()])
    orientation = SelectField('Orientation', choices=[('horizontal', 'Horizontal'), ('vertical', 'Vertical')], validators=[DataRequired()])
    submit = SubmitField('Submit')

