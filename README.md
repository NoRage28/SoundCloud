# SoundCloud Tutorial

SoundCloud project is a project that allows you to upload, find, listen, and download music.

## Table of Contents
* [Functionality](#functionality)
* [Features](#features)
* [Tools](#tools)
* [How to use](#how-to-use)
* [Possible Improvements](#possible-improvements)

## Functionality
* Base authorization and authorization with Spotify
* Email verification and the possibility to recover passwords with the email
* Editing a user profile
* Creating, editing, and deleting:
    * Licenses
    * Tracks
    * Albums
    * Playlists
* Uploading, listening, and downloading tracks
* Comments by tracks

## Features
* Custom user model
* Custom JWT authorization
* Custom validators for uploading files
* Documentation using drf_spectacular
* Tests for all endpoints

## Tools
* Phyton >= 3.10
* Django
* Django Rest Framework
* Postgres
* Docker
* Nginx

## How to use
### For use with docker
1) In the root folder create file `.env` and pass your settings
2) Create and run a docker image:

`docker-compose up --build`

3) Create a superuser:

`docker exec -it sound_cloud_web bash`

`python manage.py createsuperuser`

4) For comfortable work use documentation to the link below:

`http://localhost/api/schema/docs/`

### For use without docker
1) Create a virtual environment in the root folder:

`python3 -m venv <your_env_name>` - Linux

`python -m venv <your_env_name>` - Windows

2) Activate a virtual environment:

`source <your_env_name>/bin/activate` - Linux

`<your_env_name>\Scripts\activate.bat`- Windows

3) Upgrade pip:

`pip install --upgrade pip`

4) Install all required modules and libraries:

`pip install -r requirements.txt`

5) Make migrations in DB:

`python manage.py makemigrations`

`python manage.py migrate`

6) Create a superuser:

`python manage.py createsuperuser`

7) Run the app with the command:

`python manage.py runserver`

8) For comfortable work use documentation to the link below:

`http://localhost/api/schema/docs/`

## Possible improvements
* Add front end
