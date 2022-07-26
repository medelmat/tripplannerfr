from flask import Flask, render_template, url_for, redirect, session, request
import forms
import sys
from amadeus import Client, ResponseError
import os, ssl
from tripplanner import build_plans
import json
import pickle
from booking_scraper import bkscraper, yelpscraper
from amadeus_flights import get_flights

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

amadeus = Client(
	client_id = 'oXSVNER0itvY7GNyL8TcU9CNtGfXD9lb',
	client_secret= '40T99jNGeYjSVgm6'
)


app = Flask(__name__)
app.config['SECRET_KEY'] = '25d9c9aa3bd5819afceebc5d3f1b0399d0b6deea07928f55'
app.config['WTF_CSRF_ENABLED'] = False


@app.route('/')
def home():
	"""Landing page."""
	return redirect("/bookinghotel")


@app.route('/bookinghotel', methods=["GET", "POST"])
def bookinghotel():
	""" Standard `booking hotel` form. """
	form = forms.searchHotelsOffers()
	print(form.validate_on_submit())
	print(form.errors)
	if form.validate_on_submit():
		print('hello', file=sys.stdout)
		if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
			ssl._create_default_https_context = ssl._create_unverified_context

		depart = form.depart_city.data
		destination = form.destination_city.data
		depart_date = form.departure_date.data
		destination_date = form.arrival_date.data
		adults = form.number_pers.data

		hotels_offers = bkscraper.get_result(city=destination, people=int(adults), datein=depart_date, dateout=destination_date,limit=1, detail=True)
		flights_offers = get_flights(depart, destination, depart_date, destination_date, adults)
		restaurants_offers = yelpscraper.get_result(city=destination, limit=1, detail=True)

		with open("hotels_offers.json", 'w', encoding='utf-8') as f:
		    json.dump(hotels_offers[0], f, ensure_ascii=False, indent=4)
		    f.close()
		with open("flights_offers.json", 'w', encoding='utf-8') as f:
		    json.dump(flights_offers, f, ensure_ascii=False, indent=4)
		    f.close()
		with open("restaurants_offers.json", 'w', encoding='utf-8') as f:
		    json.dump(restaurants_offers[0], f, ensure_ascii=False, indent=4)
		    f.close()

		print(depart, destination, depart_date, destination_date, adults)

		plans = build_plans('hotels_offers.json', 'flights_offers.json', 'restaurants_offers.json')
		with open('plans.pickle', 'wb') as handle:
			pickle.dump(plans, handle)
		
		return render_template("plansresult.jinja2", plans=plans)
	return render_template(
		"bookinghotel.jinja2",
		form = form,
		template = "form-template"
		)
@app.route('/plandetail/<id>', methods=["GET"])
def plandetail(id):

	with open('plans.pickle', 'rb') as handle:
		plans = pickle.load(handle)

	#print(plans)
	#plan = next((plan for plan in plans if plan['id'] == id), None)
	res = None
	for plan in plans:
	    if plan['id'] == int(id):
	        res = plan
	        print(res)
	        break

	return render_template("plan_detail.jinja2", plan=res)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug=True)