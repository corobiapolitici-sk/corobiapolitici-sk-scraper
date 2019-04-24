from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

#################
# SCRAPE TOOLS  #
#################


def get_soup(url):
    """
    Attempt to get the content at `url` by making an HTTP GET request.

    If the content-type of response is some kind of HTML/XML, return the
    soup content, otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return BeautifulSoup(resp.content, "html.parser")
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """Return true if the response seems to be HTML, false otherwise."""
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """Print the error."""
    print(e)

#######################
# STRING MANIPULATION #
#######################


def remove_multiple_spaces(s):
    """Replace multiple spaces between words by a single space."""
    new_s = s.replace("  ", " ")
    while(len(new_s) < len(s)):
        s = new_s
        new_s = s.replace("  ", " ")
    return s


def change_name_order(name):
    """Change surname, name representation to name surname. Discard commas."""
    delimiter = "," if "," in name else " "
    names = [s.strip() for s in name.split(delimiter)]
    return " ".join(names[::-1])


def parse_date_csv(str_date):
    """Format standard date string to neo4j format."""
    parts = str_date.split(" ")
    day = parts[0][:-1]
    if len(day) == 1:
        day = "0" + day
    month = parts[1][:-1]
    if len(month) == 1:
        month = "0" + month
    year = parts[2]
    return year + month + day


def parse_datetime_csv(str_date):
    """Format standard datetime string to neo4j format."""
    res = parse_date_csv(str_date) + "T"
    res += "".join(str_date.split(" ")[3].split(":"))
    return res
