NeoPixel Fun
------------

Display clocks, animations, scrolling text, maybe even youtube videos on 
your Neopixel (WS2812 array) display! Mine is 16x8 pixels and that is plenty enough to display a nearly hd-quality video.

Arduino slave

Python host


Ubuntu
======

Install python3 with python3-setuptools.

    $ sudo apt-get install python3 python3-setuptools

This will give you the commands python3 and easy_install3.

Install pip using Python 3's setuptools: run 

    $ sudo easy_install3 pip

this will give you the command pip3.2 (or pip-3.2 on raspbian).

Install your PyPI package pyserial: run 

    $ sudo pip3.2 install pyserial 

Note: pip3.2 might be named something else, type 'pip', then tab to 
autocomplete.

You might need to upgrade pyserial. Version 2.6 is old and gives problems.
To upgrade::

    $ sudo pip3.2 install --upgrade pyserial


Configuration
=============

Make a settings.json to configure the com port, it should contain something like::

{"com_port": "/dev/tty.usbmodemfd12111"}