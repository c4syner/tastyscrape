from datetime import date, datetime
from typing import List, Text, Dict
from decimal import Decimal
import re

from tastyscrape.bases import static_option_chain
from tastyscrape.bases.session import TastyAPISession
from tastyscrape.bases.underlying import Underlying
from tastyscrape.bases.underlying import UnderlyingType
from tastyscrape.bases.option import Option
from tastyscrape.bases.option import OptionType

def get_all_expirations(session: TastyAPISession, underlying: Underlying) -> List:
    # Returns all expirations available for a defined underlying
    this_chain = static_option_chain.get_option_chain(session,underlying)
    return this_chain.get_all_expirations()

def get_all_strikes(session: TastyAPISession, underlying: Underlying, expiration: date) -> List:
    #Returns all strikes available for a defined underlying and expiration
    this_chain = static_option_chain.get_option_chain(session,underlying,expiration)
    return this_chain.get_all_strikes()

def get_option_from_dxfeed(dxstr: Text, type: UnderlyingType) -> Option:
    #Convert Option Object to dxfeed string.
    parsed = re.compile("(\.)([A-Z.]+)(\d{2})(\d{2})(\d{2})([CP])([\d.]+)").match(dxstr)
    yr = int(parsed[3])+round(datetime.now().year-49,-2) if int(parsed[3])+round(datetime.now().year-49,-2) > datetime.now().year-round(datetime.now().year-49,-2) else int(parsed[3])+round(datetime.now().year-49,-2) + 100
    ot = OptionType.PUT if parsed[6] == "P" else OptionType.CALL
    return Option(ticker=parsed[2], expiry=date(year=yr,month=int(parsed[4]),day=int(parsed[5])), strike=Decimal(str(parsed[7])), option_type=ot, underlying_type=type)

def parse_chain(resp_chain: List[Dict], type: UnderlyingType) -> List[Dict]:
    #Ddds Option object to new "option" key in every response dictionary.
    ichain = []
    for option in resp_chain:
        obj = get_option_from_dxfeed(option["eventSymbol"], type=type)
        option["option"] = obj
        ichain.append(option)
    return ichain

def split_chain(resp_chain: List[Dict]) -> Dict:
    #Split up a list of options into puts and calls by their respective keys.
    idict = {
        "calls": [],
        "puts": []
    }
    for item in resp_chain:
        if(item["option"].option_type == OptionType.PUT):
            idict["puts"].append(item)
        else:
            idict["calls"].append(item)
    return idict