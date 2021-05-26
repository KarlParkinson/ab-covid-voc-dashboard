import requests
import json
import urllib.request
import boto3
import os
import time
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup

def get_raw_cases_data():
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    req = urllib.request.Request("https://www.alberta.ca/stats/covid-19-alberta-statistics.htm", None, headers)
    contents = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(contents)

    total_cases = soup.select("#total-cases")
    cases_JSON = total_cases[0].find_all("div", class_="figure")[2].find("script").contents[0]

    cases_JSON = json.loads(cases_JSON)
    dates = cases_JSON["x"]["data"][0]["x"]
    cases = cases_JSON["x"]["data"][0]["y"]

    return [dates, cases]

def scrape_daily_all_cases():
    dates, cases = get_raw_cases_data()
    daily_cases_dict = {}
    for i in range(len(dates)):
        date = dates[i]
        date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
        daily_cases_dict[date.strftime("%Y-%m-%d")] = cases[i]

    return daily_cases_dict

def calculate_weekly_all_cases(daily_cases, start_date, end_date):
    week = 1
    current_week_days_counted = 0

    weekly_all_cases = {}
    weekly_sum = 0
    for dt in daterange(start_date, end_date):
        weekly_sum += daily_cases[dt.strftime("%Y-%m-%d")]

        current_week_days_counted += 1
        if (current_week_days_counted%7 == 0):
            current_week_days_counted = 0
            weekly_all_cases[str(week)] = weekly_sum
            week += 1
            weekly_sum = 0

    weekly_all_cases[str(week)] = weekly_sum
    return weekly_all_cases

def should_keep(row):
    if row["Date"] == "Total" or row["Date"] == "Updated" or row["Date"] == " " or row["Date"] == "":
        return False
    elif (row["AB_B117"] == " " or row["AB_B117"] == "") and (row["AB_B1351"] == " " or row["AB_B1351"] == "") and (row["AB_P1"] == " " or row["AB_P1"] == "") and (row["AB_B1617"] == " " or row["AB_B1617"] == ""):
        return False
    else:
        return True

def convert_date(excel_date):
    dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(float(excel_date)) - 2)
    return dt

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

def fill_in_missing_dates(b117_dict, b1351_dict, p1_dict, b1617_dict, start_date, end_date):
    most_recent_b117_cases = 0.0
    most_recent_b1351_cases = 0.0
    most_recent_p1_cases = 0.0
    most_recent_b1617_cases = 0.0

    b117_dict_cum= {}
    b1351_dict_cum= {}
    p1_dict_cum= {}
    b1617_dict_cum = {}
    all_cum = {}

    for dt in daterange(start_date, end_date):
        if dt.strftime("%Y-%m-%d") in b117_dict.keys():
            most_recent_b117_cases = b117_dict[dt.strftime("%Y-%m-%d")]

        if dt.strftime("%Y-%m-%d") in b1351_dict.keys():
            most_recent_b1351_cases = b1351_dict[dt.strftime("%Y-%m-%d")]

        if dt.strftime("%Y-%m-%d") in p1_dict.keys():
            most_recent_p1_cases = p1_dict[dt.strftime("%Y-%m-%d")]

        if dt.strftime("%Y-%m-%d") in b1617_dict.keys():
            most_recent_b1617_cases = b1617_dict[dt.strftime("%Y-%m-%d")]

        b117_dict_cum[dt.strftime("%Y-%m-%d")] = most_recent_b117_cases
        b1351_dict_cum[dt.strftime("%Y-%m-%d")] = most_recent_b1351_cases
        p1_dict_cum[dt.strftime("%Y-%m-%d")] = most_recent_p1_cases
        b1617_dict_cum[dt.strftime("%Y-%m-%d")] = most_recent_b1617_cases
        all_cum[dt.strftime("%Y-%m-%d")] = most_recent_p1_cases + most_recent_b117_cases + most_recent_b1351_cases + most_recent_b1617_cases

    return [b117_dict_cum, b1351_dict_cum, p1_dict_cum, b1617_dict_cum, all_cum]

def caclculate_daily_voc_cases(b117_dict_cum, b1351_dict_cum, p1_dict_cum, b1617_dict_cum, start_date, end_date):
    most_recent_b117_cases = 0.0
    most_recent_b1351_cases = 0.0
    most_recent_p1_cases = 0.0
    most_recent_b1617_cases = 0.0

    b117_dict_daily = {}
    b1351_dict_daily = {}
    p1_dict_daily = {}
    b1617_dict_daily = {}
    all_daily = {}

    for dt in daterange(start_date, end_date):
        b117_cum_cases_on_day = b117_dict_cum[dt.strftime("%Y-%m-%d")]
        b1351_cum_cases_on_day = b1351_dict_cum[dt.strftime("%Y-%m-%d")]
        p1_cum_cases_on_day = p1_dict_cum[dt.strftime("%Y-%m-%d")]
        b1617_cum_cases_on_day = b1617_dict_cum[dt.strftime("%Y-%m-%d")]

        b117_cases_reported_on_day = b117_cum_cases_on_day - most_recent_b117_cases
        b1351_cases_reported_on_day = b1351_cum_cases_on_day - most_recent_b1351_cases
        p1_cases_reported_on_day = p1_cum_cases_on_day - most_recent_p1_cases
        b1617_cases_reported_on_day = b1617_cum_cases_on_day - most_recent_b1617_cases

        b117_dict_daily[dt.strftime("%Y-%m-%d")] = b117_cases_reported_on_day
        b1351_dict_daily[dt.strftime("%Y-%m-%d")] = b1351_cases_reported_on_day
        p1_dict_daily[dt.strftime("%Y-%m-%d")] = p1_cases_reported_on_day
        b1617_dict_daily[dt.strftime("%Y-%m-%d")] = b1617_cases_reported_on_day
        all_daily[dt.strftime("%Y-%m-%d")] = b117_cases_reported_on_day + b1351_cases_reported_on_day + p1_cases_reported_on_day + b1617_cases_reported_on_day

        most_recent_b117_cases = b117_cum_cases_on_day
        most_recent_b1351_cases = b1351_cum_cases_on_day
        most_recent_p1_cases = p1_cum_cases_on_day
        most_recent_b1617_cases = b1617_cum_cases_on_day

    return b117_dict_daily, b1351_dict_daily, p1_dict_daily, b1617_dict_daily, all_daily

def caclculate_weekly_voc_cases(b117_dict_daily, b1351_dict_daily, p1_dict_daily, b1617_dict_daily, start_date, end_date):
    week = 1
    current_week_days_counted = 0

    b117_weekly = {}
    b1351_weekly = {}
    p1_weekly = {}
    b1617_weekly = {}
    all_weekly = {}

    b117_weekly_sum = 0
    b1351_weekly_sum = 0
    p1_weekly_sum = 0
    b1617_weekly_sum = 0
    for dt in daterange(start_date, end_date):
        b117_weekly_sum += b117_dict_daily[dt.strftime("%Y-%m-%d")]
        b1351_weekly_sum += b1351_dict_daily[dt.strftime("%Y-%m-%d")]
        p1_weekly_sum += p1_dict_daily[dt.strftime("%Y-%m-%d")]
        b1617_weekly_sum += b1617_dict_daily[dt.strftime("%Y-%m-%d")]

        current_week_days_counted += 1
        if (current_week_days_counted%7 == 0):
            current_week_days_counted = 0

            b117_weekly[str(week)] = b117_weekly_sum
            b1351_weekly[str(week)] = b1351_weekly_sum
            p1_weekly[str(week)] = p1_weekly_sum
            b1617_weekly[str(week)] = b1617_weekly_sum
            all_weekly[str(week)] = b117_weekly_sum + b1351_weekly_sum + p1_weekly_sum + b1617_weekly_sum

            week += 1

            b117_weekly_sum = 0
            b1351_weekly_sum = 0
            p1_weekly_sum = 0
            b1617_weekly_sum = 0

    if (current_week_days_counted%7 != 0):
        b117_weekly[str(week)] = b117_weekly_sum
        b1351_weekly[str(week)] = b1351_weekly_sum
        p1_weekly[str(week)] = p1_weekly_sum
        b1617_weekly[str(week)] = b1617_weekly_sum
        all_weekly[str(week)] = b117_weekly_sum + b1351_weekly_sum + p1_weekly_sum + b1617_weekly_sum

    return b117_weekly, b1351_weekly, p1_weekly, b1617_weekly, all_weekly

def calculate_rolling_7_day_daily_voc_average(voc_dict):
    window_size = 7
    averages = {}
    series = list(voc_dict.values())
    first_date = list(voc_dict.keys())[0]
    average_date = datetime.strptime(first_date, "%Y-%m-%d") + timedelta(days=7)

    i = 0
    while i < len(series) - window_size + 1:
        this_window = series[i : i + window_size]
        window_average = sum(this_window) / window_size

        averages[average_date.strftime("%Y-%m-%d")] = round(window_average, 2)
        average_date += timedelta(days=1)
        i += 1

    return averages

def save_webpage(s3_client):
    url = "https://www.alberta.ca/covid-19-alberta-data.aspx"
    contents = requests.get("https://www.alberta.ca/covid-19-alberta-data.aspx")
    date = datetime.now(timezone(-timedelta(hours=7)))

    s3_client.Object("covid-ab-data", "alberta_covid_html/alberta-covid-" + date.strftime("%Y-%m-%d") + ".html").put(Body=contents.text)

def invalidate_cache(aws_access_key_id, aws_secret_access_key, distribution_id):
    cloudfront = boto3.client("cloudfront", region_name="us-east-1", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    response = cloudfront.create_invalidation(DistributionId=distribution_id, InvalidationBatch={"Paths": {"Quantity": 2, "Items": ["/voc.json", "/daily_cases.json"]}, "CallerReference": str(time.time())})
    print(response)

def lambda_handler(event, context):
    all_daily_cases = scrape_daily_all_cases()
    most_recent_reporting_date = list(all_daily_cases.keys()).pop()
    all_weekly_cases = calculate_weekly_all_cases(all_daily_cases, datetime(2021, 1, 25), datetime.strptime(most_recent_reporting_date, "%Y-%m-%d"))

    response = json.loads(requests.get("https://beta.ctvnews.ca/content/dam/common/exceltojson/COVID-Variants.txt").text)
    parsed_ab_data = filter(should_keep, response)
    b117_dict = {}

    b1351_dict = {}

    p1_dict = {}

    b1617_dict = {}

    b117_dict["2020-12-15"] = 1.0
    b117_dict["2021-01-07"] = 3.0
    b117_dict["2021-01-12"] = 5.0
    b117_dict["2021-02-19"] = 13.0

    b1351_dict["2021-01-08"] = 1.0
    b1351_dict["2021-01-19"] = 2.0

    for row in parsed_ab_data:
        date = convert_date(row["Date"])
        if (row["AB_B117"] != " " and row["AB_B117"] != ""):
            b117_dict[date.strftime("%Y-%m-%d")] = float(row["AB_B117"])


        if (row["AB_B1351"] != " " and row["AB_B1351"] != ""):
            b1351_dict[date.strftime("%Y-%m-%d")] = float(row["AB_B1351"])


        if (row["AB_P1"] != " " and row["AB_P1"] != ""):
            p1_dict[date.strftime("%Y-%m-%d")] = float(row["AB_P1"])

        if (row["AB_B1617"] != " " and row["AB_B1617"] != ""):
            b1617_dict[date.strftime("%Y-%m-%d")] = float(row["AB_B1617"])

    # For easter weekend, assumed everything non-P1 is B117. Used https://twitter.com/cspotweet
    # as source, but had to add more cases on Monday to make everything add up. These numbers are likely not
    # completely correct, but it will shake out in the 7-day avg.
    b117_dict["2021-04-02"] = 4649
    b117_dict["2021-04-03"] = 5149
    b117_dict["2021-04-04"] = 5749
    b117_dict["2021-04-05"] = 6223

    b117_dict_cum, b1351_dict_cum, p1_dict_cum, b1617_dict_cum, all_cum = fill_in_missing_dates(b117_dict, b1351_dict, p1_dict, b1617_dict, datetime(2020, 12, 15), datetime.strptime(most_recent_reporting_date, "%Y-%m-%d"))
    b117_dict_daily, b1351_dict_daily, p1_dict_daily, b1617_dict_daily, all_daily = caclculate_daily_voc_cases(b117_dict_cum, b1351_dict_cum, p1_dict_cum, b1617_dict_cum, datetime(2020, 12, 15), datetime.strptime(most_recent_reporting_date, "%Y-%m-%d"))
    b117_weekly, b1351_weekly, p1_weekly, b1617_weekly, all_weekly = caclculate_weekly_voc_cases(b117_dict_daily, b1351_dict_daily, p1_dict_daily, b1617_dict_daily, datetime(2021, 1, 25), datetime.strptime(most_recent_reporting_date, "%Y-%m-%d"))
    rolling_averages = calculate_rolling_7_day_daily_voc_average(all_daily)

    variants_dict = {}
    variants_dict["B117"] = {"Cumulative": b117_dict_cum, "Daily": b117_dict_daily, "Weekly": b117_weekly}
    variants_dict["B1351"] = {"Cumulative": b1351_dict_cum, "Daily": b1351_dict_daily, "Weekly": b1351_weekly}
    variants_dict["P1"] = {"Cumulative": p1_dict_cum, "Daily": p1_dict_daily, "Weekly": p1_weekly}
    variants_dict["B1617"] = {"Cumulative": b1617_dict_cum, "Daily": b1617_dict_daily, "Weekly": b1617_weekly}
    variants_dict["All VOC"] = {"Cumulative": all_cum, "Daily": all_daily, "7 Day Daily Average": rolling_averages, "Weekly": all_weekly}

    all_cases_dict = {"Daily": all_daily_cases, "Weekly": all_weekly_cases}

    aws_access_key_id = os.environ["S3_AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = os.environ["S3_AWS_SECRET_ACCESS_KEY"]
    s3 = boto3.resource(service_name="s3", region_name="us-east-1", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    s3.Object("covid-ab-data", "voc.json").put(Body=json.dumps(variants_dict, indent=2))
    s3.Object("covid-ab-data", "daily_cases.json").put(Body=json.dumps(all_cases_dict, indent=2))

    save_webpage(s3)

    invalidate_cache(aws_access_key_id, aws_secret_access_key, os.environ["CLOUDFRONT_DISTRIBUTION_ID"])

    return {
        "statusCode": 200
    }
