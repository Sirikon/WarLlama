# Alpaca #

## Requirements ##

 - Node 6.X.X
 - Python >2.7
    - If you're using Anaconda with Python 3,  [maybe this is helpful](http://stackoverflow.com/questions/24405561/how-to-install-2-anacondas-python-2-7-and-3-4-on-mac-os-10-9)
 - Yarn (`npm install -g yarn`)

## Setup ##

 1. Go to Alpaca's root folder
 2. Run `yarn`, this will install front-end dev dependencies.
 3. Go to `src` folder
 4. Run `pip install -r requirements.txt`

## Run ##

 1. In root folder, run `npm run dev`, this will start the sass development environment with hot reload
 2. In `src` folder, run `python manage.py runserver 0.0.0.0:8080`
