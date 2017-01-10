To set up an Apache2 web server with PHP and the MongoDB driver, open a terminal and run the following commands:

sudo apt-get update
sudo apt-get install apache2 
sudo apt-get install libapache2-mod-php5
sudo apt-get install php-pear
sudo apt-get install php5-dev
sudo apt-get install libpcre3-dev
pecl install mongodb
nano /etc/php5/apache2/php.ini

Once you are in the php.ini file paste the following (do NOT add a semicolon before this and do NOT put a space before or after the equal sign):

extension=mongodb.so

tickLen is the time in ms between two ticks on the slider
The speed in ms at which the slider moves between ticks is equivalent to tickLen/speed
