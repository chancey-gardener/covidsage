#!/usr/bin/python3
# coding: utf8

# load a sql database in memory for testing yer
# good old COVID stat bot

import sqlite3
import csv
import json
import re
from itertools import chain
from os import path
from os import listdir as ls
#import progressbar
from unicodedata import normalize
#from utils import *


VERBOSE = False

DATAPATH = "/home/chanceygardener/repos/COVID-19"

# date format detection regexes
coarse_form = re.compile(r'(?P<month>\d{1,2})'
                         r'\/(?P<day>\d{1,2})\/'
                         r'(?P<year>\d{2}|\d{4})'
                         r' (?P<hour>\d{1,2}):'
                         r'(?P<minute>\d{1,2})')

TYPE_SCHEMA = (
    "text",
    "text",
    "text",
    "text",
    "qty",
    "qty",
    "qty",
    "qty",
    "qty",
    "qty"
)

SCHEMA = {
    'Province/State': 0,
    'Country/Region': 1,
    'Last Update': 2,
    'Confirmed': 3,
    'Deaths': 4,
    'Recovered': 5,
    'Latitude': 6,
    'Longitude': 7

}

PROJECT_ROOT = '/home/chanceygardener/projects/sage/backends/covid'

with open(path.join(PROJECT_ROOT, 'crosswalks', 'states_to_abbreviations.json')) as jfile:
    # maps us states to abbreviations since these
    # aren't uniformly represented in the same way
    STATES_TO_ABBREVIATIONS = json.loads(jfile.read())
with open(path.join(PROJECT_ROOT, 'crosswalks', 'metro_to_counties.json')) as jfile:
    # Crosswalk from city keywords to list of counties
    # if they are only represented as such in the dataset
    SPECIAL_METRO_AREAS = json.loads(jfile.read())


class CsvFormatError(Exception):
    pass


class InvalidDateFormatError(Exception):
    pass


INIT_DB_QUERY = """CREATE TABLE daily_instance
                    (record_date text, city_county text, 
                    province_state text, country text, 
                     confirmed real, deaths real,
                      recovered real,  active real, 
                      longitude real, latitude real);
                 """

fine_schema = (b"FIPS",   b"Admin2",  b"Province_State",
               b"Country_Region",  b"Last_Update", b"Lat", b"Long_", b"Confirmed",
               b"Deaths",  b"Recovered",   b"Active",
               b"Combined_Key")

coarse_schema = (b'Province/State', b'Country/Region',
                 b'Last Update', b'Confirmed',
                 b'Deaths', b'Recovered', b'Latitude', b'Longitude')

coarse_schema_trunc = (b'Province/State', b'Country/Region',
                       b'Last Update', b'Confirmed',
                       b'Deaths', b'Recovered')


def coarse_date_to_iso(datestring):
    re_match = re.match(coarse_form, datestring)
    if not re_match:
        raise InvalidDateFormatError(datestring)
    parsed = re_match.groupdict()
    month = parsed['month'].zfill(2)
    day = parsed['day'].zfill(2)
    hour = parsed['hour'].zfill(2)
    minute = parsed['minute'].zfill(2)
    year = parsed['year']
    if len(year) == 2:
        year = "20" + year
    odate = "-".join([year, month, day])
    # seconds not reported in this format
    otime = ":".join([hour, minute, "00"])
    return odate + "T" + otime


def process_combinedkey(k):
    out = [None, None, None]
    seq = [e.strip() for e in k.split(',')]
    out[-1] = seq[-1]
    #out[-1] = seq[0]
    if len(seq) == 2:
        out[1] = seq[0]
        #out[-1] = seq[-1]
    elif len(seq) == 3:
        out[0], out[1] = seq[0], seq[1]
    elif len(seq) > 3:
        raise CsvFormatError("unrecognized combined key")
    return out
    #out[-1] = seq[-1]


def normalize_state(state_string):
    if state_string in STATES_TO_ABBREVIATIONS.keys():
        return STATES_TO_ABBREVIATIONS[state_string]
    return state_string


def process_fine_schema(datarow):
    city_county, province_state, country = process_combinedkey(
        datarow[fine_schema.index(b"Combined_Key")])

    if province_state is not None:
        # print(province_state)
        province_state = normalize_state(
            province_state) if province_state.strip() else None
        # print(province_state)
        # print('\n')
    confirmed = int(datarow[fine_schema.index(b"Confirmed")])
    death_val = datarow[fine_schema.index(b"Deaths")]
    deaths = int(death_val) if death_val.strip() else None
    recovered_val = datarow[fine_schema.index(b"Recovered")]
    recovered = int(recovered_val) if recovered_val.strip() else None
    active = int(datarow[fine_schema.index(b"Active")])
    lat_val = datarow[fine_schema.index(b"Lat")]
    if not lat_val.strip():
        latitude = None
    else:
        latitude = float(lat_val)
    long_val = datarow[fine_schema.index(b"Long_")]
    if not long_val.strip():
        longitude = None
    else:
        longitude = float(long_val)
    date_val = datarow[fine_schema.index(b"Last_Update")]
    if not date_val:
        date_val = None
    else:
        if re.fullmatch(coarse_form, date_val):
            # print(date_val)
            date = coarse_date_to_iso(date_val)
            # print(date)
            # print("\n")
        else:
            date = date_val
    return [date, city_county, province_state, country,
            confirmed, deaths, recovered,
            active, longitude, latitude]


def process_province_state_coarse(k):
    '''return region, province'''
    out = [None, None]
    seq = [i.strip() for i in k.split(',')]
    if len(seq) == 2:
        out[0], out[1] = seq[0], seq[1]
    elif len(seq) == 1:
        out[1] = seq[0]
    return out


def process_coarse_schema(datarow):
    confirmed_val = datarow[coarse_schema.index(b"Confirmed")]
    if not confirmed_val.strip():
        confirmed = None
    else:
        confirmed = int(confirmed_val)
    recovered_val = datarow[coarse_schema.index(b"Recovered")]
    if not recovered_val.strip():
        recovered = None
    else:
        recovered = int(datarow[coarse_schema.index(b"Recovered")])
    deaths_val = datarow[coarse_schema.index(b"Deaths")]
    if not deaths_val.strip():
        deaths = None
    else:
        deaths = int(deaths_val)
    try:
        latitude = float(datarow[coarse_schema.index(b"Latitude")])
    except IndexError:
        latitude = None
    try:
        longitude = float(datarow[coarse_schema.index(b"Longitude")])
    except IndexError:
        longitude = None
    city_county, province_state = process_province_state_coarse(
        datarow[coarse_schema.index(b"Province/State")])
    if province_state is not None:
        # print(province_state)
        province_state = normalize_state(
            province_state) if province_state.strip() else None
        #print(province_state, "\n")
    country = datarow[coarse_schema.index(b"Country/Region")]
    active = None
    date_val = datarow[coarse_schema.index(b"Last Update")].strip()
    if not date_val:
        date_val = None
    else:
        if re.fullmatch(coarse_form, date_val):
            # print(date_val)
            date = coarse_date_to_iso(date_val)
            # print(date)
            # print("\n")
        else:
            date = date_val
    return [date, city_county, province_state, country,
            confirmed, deaths, recovered,
            active, longitude, latitude]


ETL_MAP = {  # These files have different headers,
    # this map shold contain tuple keys representing
    # observed header schemas, and function values
    # processing them into a uniform record schema
    fine_schema: process_fine_schema,
    coarse_schema: process_coarse_schema,
    coarse_schema_trunc: process_coarse_schema
}


def escape_char(string):
    ostring = string.replace("'", "\\'")
    ostring = ostring.replace('"', '\\"')
    return ostring


def generate_insert_query(datarow):
    query_frame = """INSERT INTO daily_instance 
                    (rowid, record_date, city_county, 
                    province_state, country,
                    confirmed, deaths, recovered,
                    active, longitude, latitude)
                    VALUES ({});"""
    vals = "null,"
    for tidx in range(len(TYPE_SCHEMA)):
        sql_type = TYPE_SCHEMA[tidx]
        if sql_type == "text":
            wrapper = '"{}"'
        elif sql_type == "qty":
            wrapper = "{}"
        else:
            raise ValueError("unrecognized sql type: {}".format(sql_type))
        raw_val = "null" if datarow[tidx] is None or datarow[tidx] == "" else datarow[tidx]
        # print(raw_val)
        if isinstance(raw_val, str):
            raw_val = escape_char(raw_val)
        # print(raw_val)
        v = wrapper.format(raw_val)
        vals += "{},".format(v)

    return query_frame.format(vals[:-1])


def read_csv(path, verbose=VERBOSE):
    with open(path, encoding='utf-8') as csvfile:

        reader = csv.reader(csvfile)
        dat = [row for row in reader]
    headers = dat.pop(0)
    if verbose:
        print("{} loaded\n\nheaders:\n\n{}".format(path, headers))

    return dat, headers


def write_csv(opath, dat, headers=None):
    with open(opath + ".csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        if headers:
            writer.writerow(headers)
        for row in dat:
            writer.writerow(row)
    print("wrote data to {}".format(opath + ".csv"))


def safe_execute(query):
    try:
        query_ex = c.execute(query)
    except sqlite3.OperationalError as e:
        print(query)
        raise sqlite3.OperationalError(e)
    dat = query_ex.fetchall()
    return dat


def generate_row_from_schema(dat):
    frame = [None] * len(SCHEMA)
    for value in SCHEMA:
        idx = SCHEMA.get(value)
        if idx is not None and idx < len(dat):
            frame[idx] = dat[idx]
    return frame


def clear_utf8_chars(string):
    return normalize('NFKD', string).encode('ascii', 'ignore')


def read_covid_case_data(root_path):
    # print("huuh?")
    header_check = set()
    all_dat = []

    dat_dir = (path.join(DATAPATH, "csse_covid_19_data",
                         "csse_covid_19_daily_reports"))

    file_iter = (path.join(dat_dir, p)
                 for p in ls(dat_dir) if p.endswith('.csv'))

    for fpath in file_iter:
        # print(fpath)

        dat, headers = read_csv(fpath)
        headers = tuple([clear_utf8_chars(i) for i in headers])
        # print(headers)
        data_proc = ETL_MAP[headers]
        for row in dat:
            data_row = data_proc(row)
            all_dat.append(data_row)
    return all_dat


conn = sqlite3.connect(':memory:')

c = conn.cursor()


def main(repo_path):
    c.execute(INIT_DB_QUERY)
    covid_dat = read_covid_case_data(repo_path)
    seen_it = set()

    # write this to csv real quick to just examine it

    # with open('covid_dat_dump_test.csv', 'w') as csvfile:
    #     writer = csv.writer(csvfile)
    #     headers = list(sorted((k for k in SCHEMA.keys()),
    #                           key=lambda x:  SCHEMA[x]))
    #     writer.writerow(headers)
    #     for row in covid_dat:
    #         writer.writerow(row)

    total_rows = len(covid_dat)
    print("loading data...")

    for i in range(len(covid_dat)):
        row = covid_dat[i]
        if tuple(row) in seen_it:
            print("dupe found!")
            continue
        query = generate_insert_query(row)
        c.execute(query)
    print("complete!")


def qwrap(string_list):
    return ["'{}'".format(i) for i in string_list]


def query_by_location(city_counties=None, province_states=None,
                      countries=None, special_metro_areas=None):
    headers = ['record_date', 'country', 'province_state',
               'city_county', 'confirmed', 'deaths', 'recovered']
    query_frame = """SELECT DISTINCT record_date, country, province_state,
            city_county, confirmed, deaths, recovered 
            from daily_instance 
            {}
            ORDER by datetime(record_date), province_state, city_county;"""
    where_frame = "where "
    if special_metro_areas:
        mc = []
        # lookup what counties the given metro
        # area encompasses and add them to city_counties
        for metro in special_metro_areas:
            lookup = SPECIAL_METRO_AREAS.get(metro)
            if lookup:
                mc += lookup
            else:
                print("warning metro area not found: {}".format(metro))
        city_counties = mc if not city_counties else mc + city_counties
    if countries:
        countries = qwrap(countries)
        country_statement = "country in ({})".format(", ".join(countries))
    else:
        country_statement = None
    if city_counties:
        city_counties = qwrap(city_counties)
        city_county_statement = "city_county in ({})".format(
            ", ".join(city_counties))
    else:
        city_county_statement = None
    if province_states:
        province_state_statement = "province_state in ({})".format(
            ", ".join(qwrap(province_states)))
    else:
        province_state_statement = None
    # TODO: date range specification

    criteria = [state for state in
                (country_statement, city_county_statement,
                 province_state_statement)
                if state]
    where_clause = where_frame + " and ".join(criteria)
    query = query_frame.format(where_clause)
    dat = safe_execute(query)

    return dat


def get_list(count, refer_by='city_county',
             count_by='confirmed', get_less_than=False):
    query = """
                SELECT DISTINCT {} from daily_instance
                where {} {} {} and {} != 'null';
    """.format(refer_by,
               count_by,
               '>=' if not get_less_than else '<=',
               count, refer_by)
    return safe_execute(query)


def get_stat(stat_descriptors,
             city_county,
             province_state,
             country, calc=lambda x: x, date = 'TODAY'):
    query = """SELECT  confirmed, deaths from daily_instance
            where city_county like '{}' 
            and province_state like '{}' 
            and country like '{}'
            order by record_date desc limit 1""".format(city_county,
                                                        province_state,
                                                        country)
    stats = safe_execute(query)[0]
    # calc should take the same number of arguments as elements in stats
    return calc(*stats)


def death_rate(city_county, province_state, country, date='TODAY'):
    return get_stat(['confirmed', 'deaths'],
                    city_county, province_state, country,
                    calc=lambda c, d: round(c/d, 3), date=date)


def covid_cases(city_county, province_state, country, date='TODAY'):
    return get_stat(['confirmed'], city_county,
                    province_state, country, date=date)
    

def disambiguate(name):
    possible_us_state = STATES_TO_ABBREVIATIONS.get(capitalize(name))
    query = """SELECT DISTINCT city_county, province_state, country
        from daily_instance
        where city_county like '{}' or country like '{}'
         or province_state like '{}'
        """.format(name, name, name)
    if possible_us_state:
        query += " or province_state like '{}'".format(possible_us_state)
    odat = safe_execute(query)
    return odat


main(DATAPATH)

if __name__ == "__main__":
    # INIT test code

    query = """SELECT DISTINCT record_date, province_state,
                city_county, confirmed, deaths, recovered 
                from daily_instance 
                where country == 'US'
                ORDER by datetime(record_date), province_state, city_county;"""
    headers = ['date', 'province_state', 'city_county',
               'confirmed', 'deaths', 'recovered']

    #query_ex = c.execute(query)
    #qdat = query_ex.fetchall()

    #write_csv('test_query_dat', qdat, headers=headers)

    #bay_test = query_by_location(special_metro_areas=['Bay Area'])
    #allegheny_test = query_by_location(city_counties=['Allegheny'])

    bt_headers = ['record_date', 'country', 'province_state',
                  'city_county', 'confirmed', 'deaths', 'recovered']
    #write_csv("bay_area_test", bay_test, headers=bt_headers)
    #write_csv("county_test", allegheny_test, bt_headers)

    #test_list = get_list(100)
    # print(test_list)
    this = disambiguate("san mateo county")
    print(this)
    selection = this[0]

    dr = death_rate(*selection)
    print("death rate: {}%".format(dr * 100))
