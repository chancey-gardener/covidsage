#!/usr/bin/python3

import pymysql

RDS_ENDPOINT = "covid.chs7h8vdks3r.us-west-1.rds.amazonaws.com"
PORT = 3306
PSSWD = 'covidkey'
group = 'default-vpc-28ff184e'

dbcon = pymysql.connect(RDS_ENDPOINT,
                        user='sage',
                        password=PSSWD,
                        db='covid')
