import logging
import sys
import code
import csv
from ib.ext.Contract import Contract
from ib.ext.Order import Order
from itertools import islice

import xml.etree.ElementTree as etree

# logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s : %(message)s')
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s %(levelname)s : %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

def make_contract(symbol, cusip=None):
    ''' create contract object '''

    logger.info('%s Contract' % symbol)

    c = Contract()
    c.m_symbol = symbol
    c.m_secType= "STK"
    c.m_exchange = "SMART"
    c.m_primaryExch = "NYSE"
    c.m_currency = "USD"
    if cusip:
        c.m_secIdType = "CUSIP" #CUSIP;SEDOL;ISIN;RIC
        c.m_secId = cusip
    
    return c

def make_order(orderId, quantity, action, fa_profile, transmit=0):
    ''' 
    create order object 

    Parameters
    -----------
    orderId : The order Id. You must specify a unique value. 
              When the order status returns, it will be identified by this tag. 
              This tag is also used when canceling the order.
    quantity: number of shares to buy or sell. Negative for sell order. 
    action: buy or sell
    fa_profile: the name of the allocation profile
    transmit: transmit immideatelly from tws
    '''

    logger.info('Placing order with id %s' % orderId)
    order_info = [action, quantity, fa_profile]
    logger.info(' | '.join(order_info))

    o = Order()

    o.m_orderId = orderId
    o.m_action = action
    o.m_totalQuantity = quantity
    o.m_transmit = transmit
    o.m_orderType = 'MKT'
    o.m_faProfile = fa_profile

    return o

class MessageHandler(object):
    ''' class for handling incoming messages '''

    def __init__(self, tws):
        self.nextValidOrderId = None
        self.last_msg = None

        tws.register(self.nextValidIdHandler,'NextValidId')
        tws.registerAll(self.debugHandler)
        
    def nextValidIdHandler(self,msg):
        ''' handles NextValidId messages '''
        self.nextValidOrderId = msg.orderId

    def debugHandler(self,msg):
        """ function to print messages """
        verbose = True
        self.last_msg = msg

        if msg.typeName == 'error' and msg.errorCode < 2000:
            if msg.errorCode == 200:
                logger.error(msg.errorMsg)
        elif verbose:
            logger.info(msg)

    def missing_cusip(self):
        if self.last_msg and self.last_msg.errorMsg == "No security definition has been found for the request":
            self.last_msg = None
            return True
        else:
            return False


def make_handler(tws):
    return MessageHandler(tws)

def generate_profile_xml(path):
  '''

  # For Potential Future Use
  # For the time being, load all the allocation files manually in TWS
  # If we want to load allocation profiles via script....

  # parser.add_argument('-a', '--allocation', help='allocation file')
  # allocation_file_path = args.allocation
  # Create Allocation Profiles
  # xml_string = generate_xml(allocation_file_path)
  
  # tws_conn.receiveFA(2, xml_string)
  # tws_conn.requestFA(2)
  # tws_conn.replaceFA(2, xml_string)

  <?xml version="1.0" encoding="UTF-8"?>
  <ListOfAllocationProfiles>
    <AllocationProfile>
      <name>BUY_GOOG_20150716</name>
      <type>3</type>
      <ListOfAllocations varName="listOfAllocations">
        <Allocation>
        <acct>DU213750</acct>
        <amount>10.0</amount>
        </Allocation>
      </ListOfAllocations>
    </AllocationProfile>
  </ListOfAllocationProfiles>
  '''

  name_header = "Profile Name,Type"
  ratio_header = "Profile,Account,Ratio"

  # Organize the allocation profile names and ratios
  with open(path) as f:
    lines = f.read().splitlines() 

  name_idx = lines.index(name_header)
  ratio_idx = lines.index(ratio_header)

  profile_names = lines[name_idx+1:ratio_idx]
  profile_ratios = lines[ratio_idx+1:len(lines)]

  # Start building the XML
  list_of_allocation_profiles = etree.Element('ListOfAllocationProfiles')

  # The Names and Ratios will have the same index
  for idx, profile_name_row in enumerate(profile_names):
    allocation_profile = etree.Element('AllocationProfile')
    name = etree.Element('name')
    child_type = etree.Element('type')

    # Build an AllocationProfile entry from the names
    profile_name = profile_name_row.split(",")[0]
    name.text = profile_name
    child_type.text = '3'

    # Build ListOfAllocations entries from the ratios
    ratio_name, ratio_account, ratio_amount = profile_ratios[idx].split(",")

    if ratio_name != profile_name:
      sys.exit("Error reading Allocation Profile")

    list_of_allocations = etree.Element("ListOfAllocations")
    list_of_allocations.attrib['varName']='listOfAllocations'
    allocation = etree.Element('Allocation')

    acct = etree.Element('acct')
    amount = etree.Element('amount')
    acct.text = ratio_account
    amount.text = ratio_amount

    allocation.append(acct)
    allocation.append(amount)
    list_of_allocations.append(allocation)

    allocation_profile.append(name)
    allocation_profile.append(child_type)
    allocation_profile.append(list_of_allocations)
    list_of_allocation_profiles.append(allocation_profile)

  return etree.tostring(list_of_allocation_profiles, encoding='unicode')

