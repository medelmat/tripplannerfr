from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, NumberRange, ValidationError
import datetime

class searchHotelsOffers(FlaskForm):
	"""Search hotels offers by City """
	depart_city = StringField(
			'Depart',
			[DataRequired()]
		)
	destination_city = StringField(
			'Destination',
			[DataRequired()]
		)
	arrival_date = DateField(
		'Date d\'arrivée'
		 )

	departure_date = DateField(
		'Date de départ'
		)
	
	number_pers = IntegerField(
		'Nb pers',
		[DataRequired(), NumberRange(min=1, max=3)]
		)

	submit = SubmitField('Validez')

	def validate_arrival_date(form, field):
		if field.data < form.departure_date.data:
			raise ValidationError("arrival date must not be earlier than departure date.")

	def validate_departure_date(form, field):		
		if field.data < datetime.date.today():
			raise ValidationError("departure date cannot be in the past.")

	def validate_destination_city(form, field):
		if field.data == form.depart_city.data:
			raise ValidationError("depart city must different from destination date.")