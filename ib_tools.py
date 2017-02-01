import logging
import sys
from ib.ext.Contract import Contract
from ib.ext.Order import Order

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

