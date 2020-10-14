from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .queries.database_queries import *
import datetime
from .exceptions.exceptions import InvalidDateRangeException, ConvertCurrencyAPIException,\
    InvalidCurrencyException, InvalidPriceException, InvalidCodeException
import requests


@api_view(['GET'])
def get_average_prices(request):
    try:
        date_from = request.GET['date_from']
        date_to = request.GET['date_to']
        origin = request.GET['origin']
        destination = request.GET['destination']

        if not is_code(origin):
            origin = get_codes_by_region_slug(origin)
        else:
            origin = "'{}'".format(origin)

        if not is_code(destination):
            destination = get_codes_by_region_slug(destination)
        else:
            destination = "'{}'".format(destination)

        pattern_date = "%Y-%m-%d"

        date_from_date_type = datetime.datetime.strptime(date_from, pattern_date)
        date_to_date_type = datetime.datetime.strptime(date_to, pattern_date)

        valid_date_range(date_from_date_type, date_to_date_type)

        response_data = get_average_price_by_date(origin, destination,
                                                  date_from_date_type.date(), date_to_date_type.date())

        return Response(status=status.HTTP_200_OK, data=response_data)

    except InvalidRegionException as ire:
        print(ire)
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={"ErrorMessage": ire.__str__()})

    except KeyError as ke:
        print(ke)
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={"ErrorMessage": f"Parameter {ke} was not sent"})

    except ValueError as ve:
        print(ve)
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={"ErrorMessage": f"The date sent is not valid {ve},"
                                              f"the expected format is YYYY-MM-DD"})

    except InvalidDateRangeException as idre:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={"ErrorMessage": idre.__str__()})

    except Exception as e:
        print(type(e))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        data={"Error Message": f"unexpect Error occurred {e}"})


@api_view(['POST'])
def add_prices(request):
    try:
        date_from = request.data['date_from']
        date_to = request.data['date_to']
        origin_code = request.data['origin_code']
        destination_code = request.data['destination_code']
        price = request.data['price']
        currency = None

        price = validate_price(price)
        validate_code(origin_code)
        validate_code(destination_code)

        if "currency" in request.data:
            currency = request.data["currency"]

        pattern_date = "%Y-%m-%d"

        date_from_date_type = datetime.datetime.strptime(date_from, pattern_date)
        date_to_date_type = datetime.datetime.strptime(date_to, pattern_date)

        valid_date_range(date_from_date_type, date_to_date_type)

        days = (date_to_date_type - date_from_date_type).days

        if currency is not None:
            price = convert_currency(price, currency)

        for i in range(days+1):
            date_insert = (date_from_date_type + datetime.timedelta(days=i)).date()
            insert_price(origin_code, destination_code, date_insert, price)

        return Response(status=status.HTTP_201_CREATED)

    except KeyError as ke:
        print(ke)
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={"ErrorMessage": f"Parameter {ke} was not sent"})

    except ValueError as ve:
        print(ve)
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={"ErrorMessage": f"The date sent is not valid {ve},"
                                              f"the expected format is YYYY-MM-DD"})

    except InvalidDateRangeException as idre:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={"ErrorMessage": idre.__str__()})

    except ConvertCurrencyAPIException as ccapie:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        data={"ErrorMessage": ccapie.__str__()})

    except InvalidPriceException as ipe:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={"ErrorMessage": ipe.__str__()})

    except InvalidCurrencyException as ice:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={"ErrorMessage": ice.__str__()})

    except InvalidCodeException as ice:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={"ErrorMessage": ice.__str__()})

    except Exception as e:
        print(type(e))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        data={"Error Message": f"unexpect Error occurred {e}"})


def valid_date_range(date_from_date_type, date_to_date_type):
    if date_from_date_type > date_to_date_type:
        raise InvalidDateRangeException(f"date_from : {date_from_date_type.date()}"
                                        f" must be smaller than date_to : {date_to_date_type.date()}")


def validate_price(price):
    try:
        return int(price)
    except Exception as e:
        raise InvalidPriceException(f"price : {price}, must be Integer ")


def convert_currency(price, currency):
    """Obs It's not appropriate to commit the app_id, it would be better to use
    some secret manager service from any cloud computing platforms
    such as aws, google cloud and so on. It could also use an environment variable,
    but to be more practical I committed the secret."""
    app_id = "937f5ffa7486464994df18739b44d492"
    response = requests.get(f"https://openexchangerates.org/api/latest.json?app_id={app_id}")
    if response.status_code != 200:
        raise ConvertCurrencyAPIException("API Not working, unable to convert currency")
    all_currencies = response.json()['rates']

    if currency not in all_currencies:
        raise InvalidCurrencyException("Invalid currency")

    return int(price * all_currencies[currency])


def validate_code(code):
    if not is_code(code):
        raise InvalidCodeException(f"Not valid code: {code}")
