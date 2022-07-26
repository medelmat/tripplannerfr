import argparse
import requests
from bs4 import BeautifulSoup
import datetime
import sys
import json
from .core.ThreadScraper import ThreadScraperV3
from .core import core
import time
from requests_ip_rotator import ApiGateway, EXTRA_REGIONS


gateway = ApiGateway("https://www.kayak.fr", regions=["eu-west-1","eu-west-2","eu-west-3"])
gateway.start()
session = requests.Session()
session.mount("https://www.kayak.fr", gateway)
today = datetime.datetime.now()
tomorrow = today + datetime.timedelta(7)

is_verbose = True

REQUEST_HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"}
BOOKING_PREFIX = 'https://www.kayak.fr'
ROW_PER_OFFSET = 16

AIRLABS_API_KEY = 'eb44e16d-e91d-4f95-bfae-0fb8d17be4ec'
SUGGEST_API_URL = 'https://airlabs.co/api/v9/suggest'

def get_city_code(city):

    airlabs_request = requests.get(SUGGEST_API_URL + '?q=' + city.strip() + "&api_key=" + AIRLABS_API_KEY)

    if airlabs_request.status_code == 200:
        return airlabs_request.json()['response']['cities'][0]['city_code']
    else: 
        return ''



def get_max_offset(soup):
    return 0


def create_url(people, depart, destination, datein, dateout, offset):

    url = "https://www.kayak.fr/flights/{depart}-{destination}" \
        "/{in_year}-{in_month}-{in_day}/{out_year}-{out_month}-{out_day}" \
        "{people}" \
        "?sort=bestflight_a" \
        .format(in_month=str(datein.month).zfill(2),
                in_day=str(datein.day).zfill(2),
                in_year=str(datein.year),
                out_month=str(dateout.month).zfill(2),
                out_day=str(dateout.day).zfill(2),
                out_year=str(dateout.year),
                people='/'+ str(people)+'adults' if int(people) > 1 else '',
                destination=destination.upper(),
                depart=depart.upper(),
                offset=offset)

    return url


def process_data(people, depart, destination, datein, dateout, is_detail, limit):
    offset = 0
    threads = []
    max_offset = 0

    starting_url = create_url(people, depart, destination, datein, dateout, offset)
    if is_verbose:
        print("[~] Url created:" + "\n" + "\t" + starting_url)
    
    response = session.get(starting_url, headers=REQUEST_HEADER)
    print(response.status_code, response.url)
    exit(0)
    time.sleep(5)
    soup = BeautifulSoup(response.text, "lxml")
    with open("/Users/Shared/Files From d.localized/ESGI4/projetannuel/api-amadeus/output.html", "w", encoding = 'utf-8') as file:
    
    # prettify the soup object and convert it into a string  
        file.write(str(soup.prettify()))
    if limit < 0:
        max_offset = int(get_max_offset(soup))
    elif limit > 0:
        max_off = int(get_max_offset(soup))
        print(max_off)
        if limit > max_off:
            max_offset = max_off
        else:
            max_offset = limit

    if is_verbose:
        print("[~] Page to fetch: " + str(max_offset))

    if is_verbose:
        print("[~] Initializing Threads...")

    if max_offset > 0:
        for i in range(int(max_offset)):
            offset += 25
            t = ThreadScraperV3(session, offset, people, depart, destination,
                              datein, dateout, is_detail, parsing_data)
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    else:
        t = ThreadScraperV3(session, offset, people, depart, destination, datein, dateout, is_detail, parsing_data)
        threads.append(t)
        t.start()
        t.join()

    return ThreadScraperV3.process_result


def parsing_data(session, people, depart, destination, datein, dateout, offset, is_detail):

    result = []
    data_url = create_url(people, depart, destination, datein, dateout, offset)
    print(data_url)

    response = session.get(data_url, headers=REQUEST_HEADER)
    soup = BeautifulSoup(response.text, "lxml")

    flights = soup.find("div", {"id" : "searchResultsList"}).select("div[class*=Base-Results-HorizonResult]")
    print("flights : ", len(flights))

   


    # print(len(soup.select_one("li.bui-pagination__pages")))
    if(is_verbose):
        print("[~] Start fetching structures")
        if(is_detail):
            print("[~] It will take a while with details")

    for hotel in hotels:
        with open("/Users/Shared/Files From d.localized/ESGI4/projetannuel/api-amadeus/hotel.html", "w", encoding = 'utf-8') as file:
    
    # prettify the soup object and convert it into a string  
            file.write(str(hotel.prettify()))
        hotel_info = {}

        hotel_info['name'] = core.get_hotel_name(hotel)

        hotel_info['score'] = core.get_hotel_score(hotel)

        hotel_info['price'] = core.get_hotel_price(hotel)

        hotel_info['link'] = core.get_hotel_detail_link(hotel)

        if hotel_info['link'] is not None:
            
            if is_detail:
                details = {}
                detail_page_response = session.get(hotel_info['link'], headers=REQUEST_HEADER)
                time.sleep(5)
                soup_detail = BeautifulSoup(detail_page_response.text, "lxml")

                details['latitude'] = core.get_coordinates(soup_detail)[0]

                details['longitude'] = core.get_coordinates(soup_detail)[1]

                details['important_facilities'] = core.get_important_facilites(soup_detail)
                print(hotel_info['link'])

                details['rooms'] = core.get_rooms(soup_detail)

                details['neighborhood_structures'] = core.get_neighborhood_structures(soup_detail)

                details['services_offered'] = core.get_services_offered(soup_detail)

                hotel_info['details'] = details

        hotel_info['thumbnail_image'] = core.get_thumbnail_image(hotel)

        result.append(hotel_info)

    if is_verbose:
        print("[~] Retrieving fetched structures")

    session.close()

    return result


def get_result(**kwargs):
    result = []
    today = datetime.datetime.now()+ datetime.timedelta(1)
    tomorrow = today + datetime.timedelta(4)

    people = kwargs.get('people', 1)
    depart = kwargs.get('depart', None)
    destination = kwargs.get('destination', None)
    datein = kwargs.get('datein', today)
    dateout = kwargs.get('datein', tomorrow)
    is_detail = kwargs.get('detail', False)
    limit = kwargs.get('limit', -1)

    if depart == None and destination == None:
        raise Exception('set the \"depart\" or \"destination\" param at least')


    if isinstance(datein, str) or isinstance(dateout, str):
        datein = datetime.datetime.strptime(datein, "%Y-%m-%d")
        dateout = datetime.datetime.strptime(dateout, "%Y-%m-%d")

    result = process_data(people, depart, destination, datein, dateout, is_detail, limit)

    return result


def retrieve_data(people, depart, destination, datein, dateout, outdir, is_detail, limit):

    result = []
    if isinstance(datein, str) or isinstance(dateout, str):
        datein = datetime.datetime.strptime(datein, "%Y-%m-%d")
        dateout = datetime.datetime.strptime(dateout, "%Y-%m-%d")

    result = process_data(people, depart, destination, datein, dateout, is_detail, limit)

    if outdir == "":
        outdir = ("./" + depart + destination + "_" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ".json").replace(" ", "_").replace(":", "_")

    if is_verbose:
        print("[~] Saving under the path: " + outdir)

    with open(outdir, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        f.close()

    print("[~] Process finished!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--people",
                        help='Used to specify the number of people to the momondo request.',
                        default=1,
                        type=int)
    parser.add_argument("--depart",
                        help='Used to specify the depart to the momondo request.',
                        default='')
    parser.add_argument("--destination",
                        help='Used to specify the destination to the momondo request.',
                        default='')
    parser.add_argument("--datein",
                        help='Used to specifiy checkin day.',
                        default=today)
    parser.add_argument("--dateout",
                        help='Used to specifiy checkout day.',
                        default=tomorrow)
    parser.add_argument("-o", "--outdir",
                        help='Used to specify the output dir and filename',
                        default="")
    parser.add_argument("-d", '--detail',
                        default=False,
                        help='Use it if you want more details in the output',
                        action='store_true')
    parser.add_argument("-v", '--verbose',
                        default=False,
                        help='Use it if you want more logs during the process',
                        action='store_true')
    parser.add_argument("-l", '--limit',
                        default=-1,
                        type=int,
                        help='Used to specify the number of page to fetch')

    args = parser.parse_args()
    if args.depart == '' and args.destination == '':
        parser.error('No action performed, use the --depart or --destination param at least')
    if args.verbose:
        is_verbose = True

    retrieve_data(args.people, args.depart, args.destination, args.datein, args.dateout, args.outdir, args.detail, args.limit)
