import json
import requests
from amadeus import Client, ResponseError

AIRLABS_API_KEY = 'eb44e16d-e91d-4f95-bfae-0fb8d17be4ec'
SUGGEST_API_URL = 'https://airlabs.co/api/v9/suggest'

#It fetches only the first page for New York city with details
amadeus = Client(
	client_id = 'oXSVNER0itvY7GNyL8TcU9CNtGfXD9lb',
	client_secret= '40T99jNGeYjSVgm6'
)

#'2022-07-19'


def get_city_code(city):

    airlabs_request = requests.get(SUGGEST_API_URL + '?q=' + city.strip() + "&api_key=" + AIRLABS_API_KEY)

    if airlabs_request.status_code == 200:
        return airlabs_request.json()['response']['cities'][0]['city_code']
    else: 
        return ''

def get_flights(depart, destination, depart_date, return_date, adults_nb):
	result = amadeus.shopping.flight_offers_search.get(originLocationCode=get_city_code(depart), destinationLocationCode=get_city_code(destination), departureDate=depart_date, returnDate=return_date, adults=adults_nb)
	flights = [] 
	for flight_offer in result.data:
		flight = {}
		flight_outbount = {}
		flight_return = {}

		flight['id'] = flight_offer['id']


		flight_outbount['duration'] = flight_offer['itineraries'][0]['duration']
		flight_outbount['steps'] = [[segment['departure']['iataCode'], segment['arrival']['iataCode'], segment['duration']] for segment in flight_offer['itineraries'][0]['segments']]
		
		flight_return['duration'] = flight_offer['itineraries'][1]['duration']
		flight_return['steps'] = [[segment['departure']['iataCode'], segment['arrival']['iataCode'], segment['duration']] for segment in flight_offer['itineraries'][1]['segments']]
		
		flight['outbound'] = flight_outbount
		flight['return'] = flight_return

		flight['price'] = flight_offer['price']['total']

		flight['availability'] = flight_offer['numberOfBookableSeats']
		flights.append(flight)

	return flights

# with open("output_flights_formatted.json", 'w', encoding='utf-8') as f:
#     json.dump(flights, f, ensure_ascii=False, indent=4)
#     f.close()