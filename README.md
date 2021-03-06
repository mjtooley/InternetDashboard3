# InternetDashboard

Dashboard of US-based ISPs using RIPE Atlas probe data to show network outages, interconnection, and performance. Designed to illustrate that all this can be measured using publicly available data without requiring network operators to collect and submit this to a reporting organization or regulator.

The dashboard is written in Python an uses MongoDB to store a local copy of the RIPE measurement results of interest.  An analysis is performed by ASN to derive network outages, interconnection (peering and transit), and performance.  The output of the analysis is written to the MongoDB as JSON formatted documents to make it easy for a website to read in the JSON data and display.  A set of webpages with HTML and Javascript are included that render the JSON data.  

Prequisites:
- MongoDB installation 
- Python 2.6
- Web server (i.e. Apache)

Installation:
- Download Python code to a working directory
- Copy the three website directories to the webserver
- Configure configuration.ini

Run:
Latest updates:
- python Internetdashboard.py -c configuration.ini

Backfill database for the dates in the configuration.ini:
- python Mongodbsave.py -c configuration.ini

Configuration.ini Parameters
- window = minutes for each sample period

Notes:
- Make sure MongoDB is running.  It may need to be started after power up with "Sudo Service Mongodb start".  Tail the log file, /var/logs/mongodb/mongodb.log.
- Verify that in data.php in /InternetDashboard3/VisualizationsDB/[Interconnect,Outage,Performance] points at the IP address of the MongoDB server.
- The Slidercontrol dates can be updated by editing the HTML files for each page
- The web pages are at:
    http://<IP address of webserver>/Outage/Outage.hmtl
    http://<IP address of webserver>/Performance/Performance.hmtl
    http://<IP address of webserver>/Interconnect/Interconnect.hmtl

sudo apt-get install python-pip
sudo pip install requests[security]
sudo pip install IPy
sudo apt-get install libffi-dev
sudo apt-get install python-numpy
sudo apt-get install libpython2.7-dev
sudo pip install ripe.atlas.sagan
sudo pip install ripe.atlas.cousteau
sudo pip install pygeoip
sudo pip install pymongo
sudo pip install geocoder
sudo pip install geoip2
sudo pip install cymruwhois
sudo apt-get install libgeoip-dev
sudo pip install python-geoip
sudo pip install ujson

