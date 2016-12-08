from ib.opt import Connection, message
from functools import partial
from time import sleep
import ib_tools as tools
import csv
import code
import argparse
import logging
import sys

#-----------Arguments-----------------

parser = argparse.ArgumentParser()
parser.add_argument('-t','--tradesfile', help='trades file')  
args = parser.parse_args()

print('Start trading script beep boop')

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)

short_sleep = partial(sleep, 1)
order_count = 0
order_errors = 0
trades_file_path = args.tradesfile #'demo_trades.csv'

if __name__ == "__main__":
  conn = Connection.create(port=7496, clientId=999)
  handler = tools.make_handler(conn)
  conn.connect()

  reader = csv.DictReader(open(trades_file_path, 'rU'), delimiter=',') # Read in trades file
  short_sleep()

  for row in reader:
    symbol, quantity, action, fa_profile, cusip = \
      row["Symbol"], row["Quantity"], row["Action"], row["Account"], row["IdValue"]

    short_sleep()
    oid = handler.nextValidOrderId + order_count

    contract = tools.make_contract(symbol, cusip)
    order = tools.make_order(oid, quantity=quantity, action=action, fa_profile=fa_profile, transmit=0)
    conn.placeOrder(oid, contract, order)

    short_sleep()
    if handler.missing_cusip():
      logger.error('Not able to find CUSIP for %s' % symbol)
      logger.info('Reloading trade using symbol as primary identifier...')
      
      oid += 1
      contract = tools.make_contract(symbol)
      order = tools.make_order(oid, quantity=quantity, action=action, fa_profile=fa_profile, transmit=0)
      conn.placeOrder(oid, contract, order)
      order_count += 1
      order_errors += 1

    order_count += 1
    short_sleep()

  conn.disconnect()

logger.info('------- Summary -------')
if order_errors == 0:
    logger.info("All %s orders were loaded successfully" % order_count)
else:
    logger.error("Some of the orders had errors, please review the logs")
