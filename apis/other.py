""" Contains functions to fetch info from different simple online APIs."""
import util.web
import xml.etree.ElementTree

def urbandictionary_search(search):
    """
    Searches urbandictionary's API for a given search term.
    :param search: The search term str to search for.
    :return: defenition str or None on no match or error.
    """
    if str(search).strip():
        urban_api_url = 'http://api.urbandictionary.com/v0/define?term=%s' % search
        response = util.web.http_get(url=urban_api_url, json=True)
        if response['json'] is not None:
            try:
                definition = response['json']['list'][0]['definition']
                return definition.encode('ascii', 'ignore')
            except (KeyError, IndexError):
                return None
    else:
        return None

def weather_search(city):
    """
    Searches worldweatheronline's API for weather data for a given city.
    You must have a working API key to be able to use this function.

    :param city: The city str to search for.
    :return: weather data str or None on no match or error.
    """
    if str(city).strip():
            city = str(city)
            api_key = '080df4dcd3105e2140eae8a066181670'
            weather_api_url = 'http://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s' % \
                              (city, api_key)

            response = util.web.http_get(url=weather_api_url, json=True)
            if response is not None:
                try:
						t = u"\u00b0" # The "degree" symbol
						w = response['json']['main']
						c = str(round(float(w['temp'] - 272.15),1)) # Conversion from Kelvin to Celsius
						f = str(round(float((w['temp'] * 9/5) - 459.67),1)) # Conversion from Kelvin to Fahrenheit
						h = str(w['humidity'])
						result = str('In {1}, the temperature is {2}{0}C or {3}{0}F with {4}% humidity').format(t, city, c, f, h)
						return result
                except (IndexError, KeyError):
                    return None
    else:
        return None


def whois(ip):
    """
    Searches ip-api for information about a given IP.
    :param ip: The ip str to search for.
    :return: information str or None on error.
    """
    if str(ip).strip():
        url = 'http://ip-api.com/json/%s' % ip
        response = util.web.http_get(url=url, json=True)
        if response['json'] is not None:
            try:
                city = response['json']['city']
                country = response['json']['country']
                isp = response['json']['isp']
                org = response['json']['org']
                region = response['json']['regionName']
                zipcode = response['json']['zip']
                info = country + ', ' + city + ', ' + region + ', Zipcode: ' + zipcode + '  Isp: ' + isp + '/' + org
                return info
            except KeyError:
                return None
    else:
        return None


def chuck_norris():
    """
    Finds a random Chuck Norris joke/quote.
    :return: joke str or None on failure.
    """
    url = 'http://api.icndb.com/jokes/random/?escape=javascript'
    response = util.web.http_get(url=url, json=True)
    if response['json'] is not None:
        if response['json']['type'] == 'success':
            joke = response['json']['value']['joke']
            return joke
        return None