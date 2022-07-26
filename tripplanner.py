import json

import pandas as pd

from forex_python.converter import CurrencyRates 
from operator import itemgetter


c = CurrencyRates()
Currency = c.get_rate('GBP', 'EUR')

def build_plans(booking_data, flight_data, restaurant_data):

	plans = []
	

	bookings = pd.read_json(booking_data)

	bookings['price'] = bookings['price'].apply(lambda x: x.replace('\xa0', ''))
	bookings['price'] = bookings['price'].apply(lambda x: float(x.split('€')[1]) if str(x).count('€')>1 else x.replace('€', ''))
	bookings['price'] = bookings['price'].apply(lambda x: float(str(x).replace('€','')) )
	#bookings['price'] = bookings['price'].apply(lambda x: round(float(x.replace('£', ''))*Currency, 2) if '£' in x else x)


	bookings_median = bookings['price'].median() * 1.01


	flights = pd.read_json(flight_data)

	flights_median = flights['price'].median() * 1.01


	restaurants = pd.read_json(restaurant_data)

	restaurants_medium = restaurants.query("price != '$$$$'")

	restaurants = restaurants.sort_values(by=['price', 'score'])

	plan_indx = 1

	for booking in bookings.sort_values(by='price').to_dict('records'):
		plan = {}

		plan['hotel'] = booking

		if booking['price'] <= bookings_median:

			plan['flight'] = flights.query("price <= @flights_median").sample().to_dict('records')[0]

			plan['restaurants'] = restaurants_medium.sample(n=3).to_dict('records')

		else:

			plan['flight'] = flights.query("price > @flights_median").sample().to_dict('records')[0]
			plan['restaurants'] = restaurants.query("price != '$$'").sample().to_dict('records')

		plan['total'] = booking['price'] + plan['flight']['price']
		plan['id'] = plan_indx
		plans.append(plan)
		plan_indx += 1




	return sorted(plans, key=lambda plan: plan.get("total"))



# with open("output_plans.json", 'w', encoding='utf-8') as f:
# 	json.dump(build_plans('output.json', 'output_flights_formatted.json', 'output_restaurant.json'), f, ensure_ascii=False, indent=4)
# 	f.close()


