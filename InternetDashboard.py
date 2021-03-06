import calendar
import time
import datetime
import ConfigParser
import getopt,sys
import threading
import logging
import logging.config
from logging.handlers import RotatingFileHandler

from NetworkOutage.NetworkOutage import networkOutage
from NetworkInterconnectMapping.NetworkInterconnectMapping import networkInterconnects
from NetworkPerformance.NetworkPerformance import PeformanceThread,perfomance_d
from configuration import getAsnList, getWindow
from SaveToMongoDB import saveToMongoDB
from StreamingResults import getStreamResults

def getstart_time():
    user_date_choice = raw_input("Enter start date. (Format: yyyy-mm-dd): ")
    user_time_choice = raw_input("Enter start time. (Format: hh:mm:ss): ")
    date_time_string = user_date_choice + " " + user_time_choice
    time_tuple = time.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
    return calendar.timegm(time_tuple)

def getend_time():
    user_date_choice = raw_input("Enter end date. (Format: yyyy-mm-dd): ")
    user_time_choice = raw_input("Enter end time. (Format: hh:mm:ss): ")
    date_time_string = user_date_choice + " " + user_time_choice
    time_tuple = time.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
    return calendar.timegm(time_tuple)

def read_start():
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('dashboard.cfg')
    start = calendar.timegm(config.get('Time', 'start')) # yyyy-mm-dd 00:00:00
    return(start)

def read_end():
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('dashboard.cfg')
    end = calendar.timegm(config.get('Time', 'end')) # yyyy-mm-dd 00:00:00
    return(end)

class streamThread(threading.Thread):
    def run(self):
        getStreamResults()


def main(argv):
    print('Internet Dashboard Starting Up...')
    configfile = ""
    try:
        opts, args = getopt.getopt(argv,"hc:",["help","config="])
    except getopt.GetoptError:
        print("Usage: Internetdashboard.py -c <config file> or Internetdashboard.py --config <config file>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print ('internetdashboard.py [-c <config file>]')
            sys.exit()
        elif opt in ("-c","--config"):
            configfile = arg

    if configfile == "":
        configfile = "configuration.ini"

    if configfile != "":
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        config.read(configfile)

        #start_string = config.get('Options', 'start')
        #date_time_string = start_string
        #time_tuple = time.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
        #start_time = calendar.timegm(time_tuple)

        #end_string = config.get('Options','end')
        #date_time_string = end_string
        #time_tuple = time.strptime(date_time_string, "%Y-%m-%d %H:%M:%S")
        #end_time = calendar.timegm(time_tuple)

        #now = int(time.time())

        # Configure the logging system
        logging.config.fileConfig('logging.conf')

        # create logger
        logger = logging.getLogger('simpleExample')

        hdlr = RotatingFileHandler('dashboard.log', maxBytes=10000000,backupCount=2)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)

        logger.info('Internet Dashboard Starting Up')

        WINDOW = getWindow()
        now = int(time.time())
        logger.info('Started at %d',now)
        start_time = (now - (now % WINDOW)) - WINDOW  # Round it to the nearest hour and back up WINDOW minutes
        end_time = now - (now % WINDOW)

        while True:
            logging.debug('Start: %s  End:%s',datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S'))
            print "Start:",datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'), " End:", datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
            logging.info('Processing for Date: %s',str(end_time - end_time % (getWindow())))
            print 'Processing for Date:',str(end_time - end_time % (getWindow()))
            startedAt = time.time() # Record the time we start this pass

            # Update the datebase with the latest results
            logger.info('Updating the database')
            print "Updating the database..."
            saveToMongoDB(start_time,end_time)

            # Compute the results and store them in them DB for the web front-end to retrieve
            #networkOutage2(end_time - WINDOW*10, end_time)
            #networkPerformance2(end_time-WINDOW*10, end_time)

#            logger.info('<=========================================================================>')
#            logger.info('Started Peformance Processing...')
#            list_of_source_asns = getAsnList()
#            threads = []
#            number_of_threads = 0

 #           for asn in list_of_source_asns:
 #               thread_name = "Performance " + str(number_of_threads + 1)
 #               thread = PeformanceThread(start_time, end_time, asn, thread_name)
 #               thread.start()
 #               threads.append(thread)
 #               number_of_threads = number_of_threads + 1

            # Wait for all the threads to finish
#            for t in threads:
 #               t.join()
            #print "All threads finished..."
#            for asn in list_of_source_asns:
#                perfomance_d(start_time, end_time, asn)
#            logger.info('Finished Peformance Processing')
#            logger.info('<=========================================================================>')

            networkOutage(start_time, end_time)
            networkInterconnects(start_time, end_time)

            start_time = end_time # move the window forward
            end_time = end_time + getWindow() # move the endtime forward a window
            # Sleep the time left from now and start of the next window
            now = int(time.time())

            # Skip ahead to the next window
            while end_time < now:
                logger.info("Catching up in time %s", end_time)
                end_time = end_time + getWindow()

            # Sleep until window
            sleep = end_time - now

            endedAt = time.time()
            loopTime = endedAt - startedAt
            logger.info('Processing time (secs): %s', loopTime)
            logger.info('Going to Sleep for %s seconds', sleep)
            logger.info('Will wake up at %s %s', end_time, datetime.datetime.fromtimestamp(time.time()+sleep).strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep(sleep) # 1800 seconds or 30 minutes
            logger.info('Awakened')

            now = int(time.time())
            end_time = start_time + getWindow() # process from where we left off last time to now

    else:

        user_choice = raw_input("Press 1 to save results to the database \n Press 2 to process results from the database \n Your choice: ")

        if user_choice == "1":
            start_time = getstart_time()
            end_time = getend_time()
            print start_time
            print end_time
            print "Saving..."
            saveToMongoDB(start_time, end_time)
            print "Fin."
        elif user_choice == "2":
            user_prompt = raw_input("You have the following choices: \n Press 1 for Network Outages (Time interval: 15 minutes) \n Press 2 for Network Performance (Time interval: 6 minutes) \n Press 3 for Network Interconnect Mapping (Time interval: 30 minutes) \n Your choice: ")

            start_time = getstart_time()
            end_time = getend_time()

            # print start_time
            # print end_time
            if user_prompt == "1":
                networkOutage(start_time, end_time)
            elif user_prompt == "2":
                networkPerformance(start_time, end_time)
            elif user_prompt == "3":
                networkInterconnects(start_time, end_time)
            else:
                print "Invalid input."
        else:
            print "Invalid input."

if __name__ == '__main__':
    main(sys.argv[1:])