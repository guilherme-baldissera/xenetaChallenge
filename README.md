# xenetaChallenge

## Requirements to execute the project
- python 3.7 (or higher version)
- Django, djangorestframework, requests, psycopg2-binary, psycopg2  (all of them are inside requirements.txt)

## Configured the database
- To configure the database modify the setting.py according with your database

- code that has to be modified :
```
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'data_base_name',
            'USER': 'user_name',
            'PASSWORD': 'password',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
```

## To run the project locally Execute the following commands
- `./manage.py runserver` (run by default into the port 8000)


## OBS
- To send a price in a different coin from USD,
 it's necessary to send the currency in the payload,
 
- currency is optional
 
 - Requests example:
 ```
POST - localhost:8000/addprices/

{
	"date_from": "2016-01-11",
	"date_to": "2016-01-15",
	"origin_code": "CNSGH",
	"destination_code": "EETLL",
	"price": "125",
	"currency" : "EUR"
}

GET http://localhost:8000/rates/?date_from=2016-01-01&date_to=2016-01-20&origin=CNSGH&destination=EETLL

```