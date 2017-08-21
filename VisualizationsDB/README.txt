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
______________

Firstly, install MongoDB. You can see it is so simple and one and only one command.

1
sudo apt-get install mongodb
To make sure that MongDB is running, you can use command below

thanhson1085@sonnst:~/projects$ ps -ef|grep mongo
245:mongodb   2870     1  4 11:52 ?        00:00:21 /usr/bin/mongod --config /etc/mongodb.conf
248:thanhso+  2905  1615  0 12:00 pts/0    00:00:00 grep --color=auto mongo
To install Mongo PHP Driver, you use the command below.

sudo pecl install mongo
The command above use Pecl, so if you machine have not installed it yet. You can install easily by the command below

sudo apt-get install php5-dev php5-cli php-pear
And now, you have to enable Mongo PHP extension by way add “extension=mongo.so” to php.ini file or use the commands below

sudo -s
echo "extension=mongo.so" > /etc/php5/mods-available/mongo.ini
php5enmod mongo
exit
Almost done, just need to check that your job is done or not.

thanhson1085@sonnst:~$ php -i|grep mongo
16:/etc/php5/cli/conf.d/20-mongo.ini,
330:mongo
343:mongo.allow_empty_keys => 0 => 0
344:mongo.chunk_size => 261120 => 261120
345:mongo.cmd => $ => $
346:mongo.default_host => localhost => localhost
347:mongo.default_port => 27017 => 27017
348:mongo.is_master_interval => 15 => 15
349:mongo.long_as_object => 0 => 0
350:mongo.native_long => 1 => 1
And writing a php script to create document, collection and insert data to mongodb.

<?php

// connect
$m = new MongoClient();

// select a database
$db = $m->test1;

// select a collection (analogous to a relational database's table)
$collection = $db->colection_test;

// add a record
$document = array( "title" => "New One", "author" => "Nguyen Sy Thanh Son" );
$collection->insert($document);

// add another record, with a different "shape"
$document = array( "title" => "The Second One", "online" => true );
$collection->insert($document);

// find everything in the collection
$cursor = $collection->find();

// iterate through the results
foreach ($cursor as $document) {
    echo $document["title"] . "\n";
}

?>
If success, the output will be same as the below

$ sudo php test.php
New One
The Second One

____________

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
