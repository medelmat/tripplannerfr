import threading


class ThreadScraper(threading.Thread):

   process_result = []

   def __init__(self, session, offset, people, country, city, datein, dateout, is_detail, parsing_data):
      threading.Thread.__init__(self)
      self.session = session
      self.offset  = offset
      self.people   = people
      self.country = country
      self.city = city
      self.datein = datein
      self.dateout = dateout
      self.is_detail = is_detail
      self.parsing_data = parsing_data

   def run(self):
      self.process_result.append(self.parsing_data(self.session, self.people, self.country, self.city, self.datein, self.dateout, self.offset, self.is_detail))

class ThreadScraperV2(threading.Thread):

   process_result = []

   def __init__(self, session, offset, city, is_detail, parsing_data):
      threading.Thread.__init__(self)
      self.session = session
      self.offset  = offset
      self.city = city
      self.is_detail = is_detail
      self.parsing_data = parsing_data

   def run(self):
      self.process_result.append(self.parsing_data(self.session, self.city, self.offset, self.is_detail))


class ThreadScraperV3(threading.Thread):

   process_result = []

   def __init__(self, session, offset, people, depart, destination, datein, dateout, is_detail, parsing_data):
      threading.Thread.__init__(self)
      self.session = session
      self.offset  = offset
      self.people   = people
      self.depart = depart
      self.destination = destination
      self.datein = datein
      self.dateout = dateout
      self.is_detail = is_detail
      self.parsing_data = parsing_data

   def run(self):
      self.process_result.append(self.parsing_data(self.session, self.people, self.depart, self.destination, self.datein, self.dateout, self.offset, self.is_detail))