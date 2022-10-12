from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import scraping


class Flight:
    leave_date = ""
    return_date = ""
    depart_time = ""
    arrive_time = ""
    airline = ""
    travel_time = ""
    origin = ""
    destination = ""
    num_stops = 0
    layover_time = ""
    stop_location = ""
    co2_emission = 0
    emission_avg_diff_percent = 0
    price = 0
    trip_type = ""
    access_date = ""

def flights_from_scrape(result):
    # result is a dict of arrays
    flights = []

    for i in range(len(result['Leave Date'])):
        flight = Flight()
        flight.leave_date = result['Leave Date'][i]
        flight.return_date = result['Return Date'][i]
        flight.depart_time = result['Depart Time (Leg 1)'][i]
        flight.arrive_time = result['Arrival Time (Leg 1)'][i]
        flight.airline = result['Airline(s)'][i]
        flight.travel_time = result['Travel Time'][i]
        flight.origin = result['Origin'][i]
        flight.destination = result['Destination'][i]
        flight.num_stops = result['Num Stops'][i]
        flight.layover_time = result['Layover Time'][i]
        flight.stop_location = result['Stop Location'][i]
        flight.co2_emission = result['CO2 Emission'][i]
        flight.emission_avg_diff_percent = result['Emission Avg Diff (%)'][i]
        flight.price = result['Price ($)'][i]
        flight.trip_type = result['Trip Type'][i]
        flight.access_date = result['Access Date'][i]
        flights.append(flight)
    return flights

origin = "YYZ"
destination_airports = ["LAS"]

# weekends defined by the saturday
weekends = ["Nov 5 2022", "Nov 12 2022", "Nov 19 2022", "Dec 3 2022", "Jan 7 2023", "Jan 21 2023", "Jan 28 2023" ]

# leave on the thursday, return on the sunday
leave_dates = [ (datetime.strptime(weekend, "%b %d %Y") - timedelta(days=2)).strftime("%Y-%m-%d") for weekend in weekends ]
return_dates = [ (datetime.strptime(weekend, "%b %d %Y") + timedelta(days=1)).strftime("%Y-%m-%d") for weekend in weekends ]


price_data = np.array([[0]*len(weekends)]*len(destination_airports))
price_data = pd.DataFrame(price_data, columns=weekends, index=destination_airports)

for j in range(len(destination_airports)):
    destination = destination_airports[j]

    result = scraping.scrape_data(origin, destination, leave_dates, return_dates, cache=False)
    flights = flights_from_scrape(result)

    for i in range(len(weekends)):
        # get all flights for this weekend
        flights_for_weekend = [flight for flight in flights if flight.leave_date == leave_dates[i]]
        # get list of flights with num_stops = 0 sorted by price low to high
        flights_for_weekend.sort(key=lambda x: x.price)
        flights_no_stops = [flight for flight in flights_for_weekend if flight.num_stops == 0]
        cheapest_nonstop_flight = None
        if len(flights_no_stops) > 0:
            cheapest_nonstop_flight = flights_no_stops[0]

        if cheapest_nonstop_flight is not None:
            price_data.loc[destination, weekends[i]] = cheapest_nonstop_flight.price
            #print(f"{cheapest_nonstop_flight.origin} to {cheapest_nonstop_flight.destination}: ${cheapest_nonstop_flight.price}")


print(price_data.to_string())
price_data.to_csv("price_data.csv")