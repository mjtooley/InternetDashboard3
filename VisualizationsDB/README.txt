To set up an Apache2 web server with PHP and the MongoDB driver, open a terminal and run the following commands:

Ubuntu 14
sudo apt-get update
sudo apt-get install apache2 
sudo apt-get install libapache2-mod-php5
sudo apt-get install php-pear
sudo apt-get install php5-dev
sudo apt-get install libpcre3-dev
pecl install mongodb
nano /etc/php5/apache2/php.ini

Ubuntu 16
sudo apt-get update
sudo apt-get install apache2
sudo apt-get install php7.0
sudo apt-get install php-pear
sudo apt-get install php-dev
sudo apt-get install libpcre3-dev
sudo apt-get install -y autoconf g++ make openssl libssl-dev libcurl4-openssl-dev
sudo apt-get install -y libcurl4-openssl-dev pkg-config
sudo apt-get install -y libsasl2-dev
pecl install mongodb
sudo pecl config-set php_ini /etc/php/7.0/apache2/php.ini

Once you are in the php.ini file paste the following (do NOT add a semicolon before this and do NOT put a space before or after the equal sign):

extension=mongodb.so

tickLen is the time in ms between two ticks on the slider
The speed in ms at which the slider moves between ticks is equivalent to tickLen/speed

Install PHP 5.6 on Ubuntu

Use the following set of command to add PPA for PHP 5.6 in your Ubuntu system and install PHP 5.6.

$ sudo apt-get install python-software-properties
$ sudo add-apt-repository ppa:ondrej/php
$ sudo apt-get update
$ sudo apt-get install -y php5.6
Check Installed PHP Version:

$ php -v

PHP 5.6.29-1+deb.sury.org~xenial+1 (cli)
Copyright (c) 1997-2016 The PHP Group
Zend Engine v2.6.0, Copyright (c) 1998-2016 Zend Technologies
    with Zend OPcache v7.0.6-dev, Copyright (c) 1999-2016, by Zend Technologies
Install PHP 7.1 on Ubuntu

Use the following set of command to add PPA for PHP 7.1 in your Ubuntu system and install PHP 7.1.

$ sudo apt-get install python-software-properties
$ sudo add-apt-repository ppa:ondrej/php
$ sudo apt-get update
$ sudo apt-get install -y php7.1
Check Installed PHP Version:

$ php -v

PHP 7.1.0-5+deb.sury.org~xenial+1 (cli) ( NTS )
Copyright (c) 1997-2016 The PHP Group
Zend Engine v3.1.0-dev, Copyright (c) 1998-2016 Zend Technologies
    with Zend OPcache v7.1.0-5+deb.sury.org~xenial+1, Copyright (c) 1999-2016, by Zend Technologies
Switch Between PHP Version’s

If you have installed multiple php versions and want to use different than default. Use following steps to switch between php5.6 and php7.1 version. You can use the same command for other php versions.

From PHP 5.6 => PHP 7.1
Apache:-

$ sudo a2dismod php5.6
$ sudo a2enmod php7.1
$ sudo service apache2 restart

CLI:-

$ update-alternatives --set php /usr/bin/php7.1
From PHP 7.1 => PHP 5.6
Apache:-

$ sudo a2dismod php7.1
$ sudo a2enmod php5.6
$ sudo service apache2 restart

CLI:-

$ sudo update-alternatives --set php /usr/bin/php5.6
