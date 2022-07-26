from bs4 import BeautifulSoup


def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def get_hotel_name(hotel):
    if hotel.find("div", {"data-testid" : "title"}) is None:
        return ''
    else:
        return hotel.find("div", {"data-testid" : "title"}).text.strip()

def get_hotel_score(hotel):
    if hotel.find("div", {"data-testid" : "review-score"}) is None:
        return ''
    else:
        return hotel.find("div", {"data-testid" : "review-score"}).text.strip()[0:3]

def get_hotel_price(hotel):
    if hotel.find("div", {"data-testid" : "price-and-discounted-price"}) is None:
        return ''
    else:
        return hotel.find("div", {"data-testid" : "price-and-discounted-price"}).text.strip()

def get_hotel_detail_link(hotel):
    if hotel.find("a", {"data-testid" : "title-link"}) is None:
        return ''
    else:
        return hotel.find("a", {"data-testid" : "title-link"})['href']

def get_coordinates(soup_detail):
    coordinates = []
    if soup_detail.select_one("#hotel_sidebar_static_map") is None:
        coordinates.append('')
        coordinates.append('')
    else:
        coordinates.append(soup_detail.select_one("#hotel_sidebar_static_map")["data-atlas-latlng"].split(",")[0])
        coordinates.append(soup_detail.select_one("#hotel_sidebar_static_map")["data-atlas-latlng"].split(",")[1])

    return coordinates

def get_important_facilites(soup_detail):

    if soup_detail.select_one("div.hp_desc_important_facilities.clearfix.hp_desc_important_facilities--bui") is None:
        return []
    else:
        return list(dict.fromkeys([service.text.strip() for service in soup_detail.findAll("div", {"class": "important_facility"})]))

def get_neighborhood_structures(soup_detail):

    neighborhood_list = []

    if soup_detail.find("div", {"class" : "hp_location_block__content_container"}) is None:
        neighborhood_list = []
    else:

        for neighborhood in soup_detail.find("div", {"class" : "hp_location_block__content_container"}).findAll('div', {"class": "hp_location_block__section_container"}):
            neighborhood_structures = {}
            neighborhood_structure_list = []
            try:
                neighborhood_structures['structure_type']= neighborhood.find("span", {"class" : "bui-title__text"}).text.strip()
            except:
                neighborhood_structures['structure_type']= ''
            
            for structure_type in neighborhood.findAll("li", {"class" : "bui-list__item"}):
                neighborhood_structure ={} 

                if structure_type.find("div", {"class": "bui-list__description"}).contents[0].strip() == '':
                    neighborhood_structure['name'] = structure_type.find("div", {"class": "bui-list__description"}).text.strip().replace("\n\n", " : ")
                else:
                    neighborhood_structure['name'] = structure_type.find("div", {"class": "bui-list__description"}).contents[0].strip()

                try:
                    neighborhood_structure['distance'] = structure_type.find('div', {"class": "bui-list__item-action hp_location_block__section_list_distance"}).text.strip()
                except:
                    neighborhood_structure['distance'] = ''

                neighborhood_structure_list.append(neighborhood_structure)
                neighborhood_structures['structure_list'] = neighborhood_structure_list

            neighborhood_list.append(neighborhood_structures)
    
    return neighborhood_list

def get_services_offered(soup_detail):

    services_offered_list = []

    if soup_detail.find("div", {"class" : "hotel-facilities__list"}) is None:
        services_offered_list = []
    else:

        for services in soup_detail.find("div", {"class" : "hotel-facilities__list"}).findAll("div", {"class" : "bui-spacer--large"}):

            services_offered = {}
            services_offered['type'] = services.find("div", {"class" : "bui-title__text hotel-facilities-group__title-text"}).text.strip()

            services_offered['value'] = []
            for checks in services.findAll("li"):

                if checks.find("div", {"class" : "bui-list__description"}) is not None:

                    services_offered['value'].append(checks.find("div", {"class" : "bui-list__description"}).text.strip())


            services_offered_list.append(services_offered)
    
    return services_offered_list

def get_rooms(soup_detail):

    rooms_list = []

    if soup_detail.select_one('#hprt-table') is None:

        rooms_list = []
    else:
        print(len(soup_detail.select_one('#hprt-table').findAll("tr")))
        for room in soup_detail.select_one('#hprt-table').find("tbody").findAll("tr"):
            room_detail ={}
            if len(room.findAll("td")) > 4:
                for a in room.select_one("td:nth-of-type(1)").findAll("a"):
                    room_detail["name"] = a.span.text.strip() if a.find("span") else ""
                    room_detail["beds"] = [bed.span.text.strip() for bed in room.findAll("li", {"class" : "rt-bed-type"})]
                    room_detail["features"] = [feature.text.strip() for feature in room.findAll("span", {"class": "hprt-facilities-facility"})]
                    room_detail["capacity"] = room.select_one("td:nth-of-type(2)").find("div").text.strip()
                    room_detail["price"] = room.select_one("td:nth-of-type(3)").find("div").text.strip().split("\n")[0]
                    room_detail["conditions"] = [condition.text.strip().replace("\n", "") for condition in room.select_one("td:nth-of-type(4)").findAll("li")]
            else:
                room_detail["name"] = rooms_list[-1]["name"]
                room_detail["beds"] = rooms_list[-1]["beds"]
                room_detail["features"] = rooms_list[-1]["features"]
                room_detail["capacity"] = room.select_one("td:nth-of-type(1)").find("div").text.strip()
                room_detail["price"] = room.select_one("td:nth-of-type(2)").find("div").text.strip().split("\n")[0]
                room_detail["conditions"] = [condition.text.strip().replace("\n", "") for condition in room.select_one("td:nth-of-type(3)").findAll("li")]
            room_detail["availability"] = max([int(value["value"]) for value in room.find("select", {"data-component" : "hotel/new-rooms-table/select-rooms"}).findAll("option")])

            rooms_list.append(room_detail)

    return rooms_list

def get_thumbnail_image(hotel):

    if hotel.find("img", {"data-testid" : "image"}) is None:
        return ''
    else:
        return hotel.find("img", {"data-testid" : "image"})['src']

def get_restaurant_name(restaurant):
    if restaurant.select_one("div[class*= businessName__09f24__EYSZE]") is None:
        return ''
    else:
        return restaurant.select_one("div[class*= businessName__09f24__EYSZE]").find("a")['name']

def get_restaurant_detail_link(restaurant):
    if restaurant.select_one("div[class*= businessName__09f24__EYSZE]") is None:
        return ''
    else:
        return restaurant.select_one("div[class*= businessName__09f24__EYSZE]").find("a")['href']

def get_restaurant_score(restaurant):
    if restaurant.select_one("div[class*= i-stars__09f24__M1AR7]") is None:
        return ''
    else:
        return restaurant.select_one("div[class*= i-stars__09f24__M1AR7]")['aria-label'].split(" ")[0]

def get_restaurant_reviews_count(restaurant):
    if restaurant.select_one("span[class*=reviewCount__09f24__tnBk4]") is None:
        return ''
    else:
        return restaurant.select_one("span[class*=reviewCount__09f24__tnBk4]").text.strip()

def get_restaurant_cuisine_type(restaurant):
    if restaurant.findAll("span", {"class": "css-dd1rsv"}) is None:
        return ''
    else:
        return ",".join([span.text.strip() for span in restaurant.findAll("span", {"class": "css-dd1rsv"})])

def get_restaurant_price(restaurant):
    if restaurant.select_one("span[class*=priceRange__09f24__mmOuH]") is None:
        return ''
    else:
        return restaurant.select_one("span[class*=priceRange__09f24__mmOuH]").text.strip()

def get_restaurant_coordinates(soup_detail):
    coordinates = []
    if soup_detail.select_one("div[class*= container__09f24__fZQnf]") is None:
        coordinates.append('')
        coordinates.append('')
    else:
        coordinates = find_between(soup_detail.select_one("div[class*= container__09f24__fZQnf]").find("img")['src'], "center=", "&").split("%2C")

    return coordinates

def get_restaurant_address(soup_detail):
    if soup_detail.find("address") is None:
        return ''
    else:
        return soup_detail.find("address").text.strip()

def get_restaurant_tel(soup_detail):
    tel = ''
    if soup_detail.select("p[class*= css-1p9ibgf]") is None:
        return tel
    else:
        for p in soup_detail.select("p[class*= css-1p9ibgf]"):
            if p.find("a") is None:
                tel= p.text.strip()

        return tel

def get_restaurant_thumbnail_image(restaurant):
    if restaurant.find("img") is None:
        return ''
    else:
        return restaurant.find("img")['srcset'].split(" ")[0]


