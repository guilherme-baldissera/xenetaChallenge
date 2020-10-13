from django.db import connection
from ..exceptions.exceptions import InvalidRegionException


def is_code(code):
    return len(code) == 5 and code.isupper()


def get_codes_by_region_slug(region_slug):
    is_valid_region(region_slug)

    all_regions = set()
    all_regions.add(region_slug)

    add_all_regions(all_regions, region_slug)

    all_regions_formatted = ",".join([f"'{region}'" for region in all_regions])

    cursor = connection.cursor()
    cursor.execute("select code from ports where parent_slug in ({})".format(all_regions_formatted))
    rows = cursor.fetchall()
    rows = [f"'{row[0]}'" for row in rows]
    return ",".join(rows)


def add_all_regions(all_regions, region_name):
    cursor = connection.cursor()
    cursor.execute("select slug from regions where parent_slug=%(region_name)s",
                   {'region_name': region_name})
    rows = cursor.fetchall()
    for row in rows:
        all_regions.add(row[0])
        add_all_regions(all_regions, row[0])


def is_valid_region(region_slug):
    cursor = connection.cursor()
    cursor.execute("select slug from regions where slug=%(region_slug)s",
                   {'region_slug': region_slug})
    rows = cursor.fetchall()
    if len(rows) == 0:
        raise InvalidRegionException(f"Invalid Region {region_slug}")


def insert_price(origin_code, destination_code, date_insert, price):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO prices (orig_code, dest_code, day, price) VALUES"
                   " (%(orig_code)s, %(dest_code)s, %(day)s, %(price)s);",
                   {'orig_code': origin_code, 'dest_code': destination_code,
                    'day': date_insert, 'price': price})


def get_average_price_by_date(origin, destination, date_from, date_to):
    cursor = connection.cursor()

    query = "SELECT day, AVG(price), COUNT(day) FROM prices WHERE orig_code in ({}) and dest_code in ({}) and" \
            " day>=%(date_from)s and day<=%(date_to)s GROUP BY day".format(origin, destination)

    cursor.execute(query, {'date_from': date_from, 'date_to': date_to})
    rows = cursor.fetchall()
    response_data = []
    for row in rows:
        if row[2] < 3:
            response_data.append({"day": row[0], "average_price": None})
        else:
            response_data.append({"day": row[0], "average_price": row[1]})

    return response_data
