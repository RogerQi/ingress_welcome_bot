# ingress_welcome_bot

## Introduction
A bot that welcome new comers of your faction! It automatically logins in and gets data from [Ingress Intel](https://www.ingress.com/intel).

It works by scanning and filtering messages from designate areas and detecting new comers with a simple regex that matches 'has completed traing', which will be automatically posted in faction comm everytime a new comer enter the game.
Then the bot'd @newcomer, greets them, and invite them to join the local ingress group!

## Dependent libraries
- [Requests](http://www.python-requests.org/en/master/)
- [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs4/)

## How to edit config.py
Config.py is a placeholder for your private parameters. The bot requires the username and the password of a google account, what you wanna send in faction comm, a set of latitudes and longitudes, and user-agent string.

While others should be easy to fill out, the latitudes and longitudes may require a few minutes to settle. I advise you to check your city on google map and make a few (or just one) rectangle that roughly include your city in it. And Remember, either latitude or longitude need to be accurate to six decimal places and decimal points need to be removed.

## Usage 
1. Make sure you have all the dependent libraries properly installed.
2. Edit config.py.
3. python ingress_rec_bot.py
4. It should be working!
