import argparse
import requests
from bs4 import BeautifulSoup
import datetime
import sys
import json
from .core.ThreadScraper import ThreadScraperV2
from .core import core
import time
from requests_ip_rotator import ApiGateway, EXTRA_REGIONS




gateway = ApiGateway("https://www.yelp.fr", regions=["eu-west-3"])
gateway.start()
session = requests.Session()
session.mount("https://www.yelp.fr", gateway)


is_verbose = True

REQUEST_HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"}
BOOKING_PREFIX = 'https://www.yelp.fr'
ROW_PER_OFFSET = 10

def get_max_offset(soup):
    all_offset = []
    if soup.select("div[class*= pagination-link-container]")  is not None:
        print(len(soup.select("div[class*= pagination-link-container]")))
        all_offset = soup.select("div[class*= pagination-link-container]")[-1].get_text().splitlines()[-1]

    return all_offset


def create_url(city):

    url = "https://www.yelp.fr/search?find_desc=Restaurants&find_loc={city}" \
        .format(city=str(city).strip().replace(" ", "+"))

    return url


def process_data(city, is_detail, limit):
    offset = 0
    threads = []
    max_offset = 0

    starting_url = create_url(city)
    print(starting_url)
    if is_verbose:
        print("[~] Url created:" + "\n" + "\t" + starting_url)


    response = session.get(starting_url, headers=REQUEST_HEADER)



    print(response.status_code, response.url)
    soup = BeautifulSoup(response.text, "lxml")

    if limit < 0:
        max_offset = int(get_max_offset(soup))
    elif limit > 0:
        max_off = int(get_max_offset(soup))
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
            offset += 30
            t = ThreadScraperV2(session, offset, city,
                               is_detail, parsing_data)
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    else:
        t = ThreadScraperV2(session, offset, city, is_detail, parsing_data)
        threads.append(t)
        t.start()
        t.join()

    return ThreadScraperV2.process_result


def parsing_data(session, city, offset, is_detail):

    result = []
    data_url = create_url(city)

    response = session.get(data_url, headers=REQUEST_HEADER)
    soup = BeautifulSoup(response.text, "lxml")

    
    restaurants = soup.findAll("div",{"data-testid": "serp-ia-card"}) 

    print(len(restaurants))
    if(is_verbose):
        print("[~] Start fetching structures")
        if(is_detail):
            print("[~] It will take a while with details")

    for restaurant in restaurants:

        restaurant_info = {}

        restaurant_info['name'] = core.get_restaurant_name(restaurant)

        restaurant_info['score'] = core.get_restaurant_score(restaurant)

        restaurant_info['reviews'] = core.get_restaurant_reviews_count(restaurant)

        restaurant_info['cuisine'] = core.get_restaurant_cuisine_type(restaurant)

        restaurant_info['price'] = core.get_restaurant_price(restaurant)

        restaurant_info['link'] = BOOKING_PREFIX + core.get_restaurant_detail_link(restaurant)

        if restaurant_info['link'] is not None:
            if is_detail:
                details = {}
                detail_page_response = session.get(restaurant_info['link'], headers=REQUEST_HEADER)

                soup_detail = BeautifulSoup(detail_page_response.text, "lxml")

                details['latitude'] = core.get_restaurant_coordinates(soup_detail)[0]

                details['longitude'] = core.get_restaurant_coordinates(soup_detail)[1]

                details['address'] = core.get_restaurant_address(soup_detail)

                details['tel'] = core.get_restaurant_tel(soup_detail)

                restaurant_info['details'] = details

        restaurant_info['thumbnail_image'] = core.get_restaurant_thumbnail_image(restaurant)

        result.append(restaurant_info)

    if is_verbose:
        print("[~] Retrieving fetched structures")

    session.close()


    return result


def get_result(**kwargs):
    result = []


    city = kwargs.get('city', None)
    is_detail = kwargs.get('detail', False)
    limit = kwargs.get('limit', -1)

    if city == None:
        raise Exception('set the \"city\"  param at least')


    result = process_data(city, is_detail, limit)

    return result


def retrieve_data(city, outdir, is_detail, limit):

    result = []


    result = process_data(city, is_detail, limit)

    if outdir == "":
        outdir = ("./"  + city + "_" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ".json").replace(" ", "_").replace(":", "_")

    if is_verbose:
        print("[~] Saving under the path: " + outdir)

    with open(outdir, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        f.close()

    print("[~] Process finished!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--city",
                        help='Used to specify the city to the yelp request.',
                        default='')
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
    if args.city == '':
        parser.error('No action performed, use the --city param at least')
    if args.verbose:
        is_verbose = True

    retrieve_data(args.city, args.outdir, args.detail, args.limit)
