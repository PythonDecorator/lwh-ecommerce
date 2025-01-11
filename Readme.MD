

# Introduction

The goal of this project is to provide minimalistic django project template that everyone can use, which _just works_ out of the box and has the basic setup you can expand on. 

Template is written with django 1.11 and python 3 in mind.

![Default Home View](__screenshots/home.png?raw=true "Title")

### Main features

* Separated dev and production settings

* Example app with custom user model

* Bootstrap static files included

* User registration and logging in as demo

* Procfile for easy deployments

* Separated requirements files

* SQLite by default if no env variable is set

# Usage

To use this template to start your own project:

### Existing virtualenv

      

      
      
After that just install the local dependencies, run migrations, and start the server.

{% endif %}

# Gimsap

# Getting Started

First clone the repository from Github and switch to the new directory:

    $ git clone git@github.com/codertjay/Gimsap.git
    $ cd Gimsap
    
Activate the virtualenv for your project.
    
Install project dependencies:

    $ pip install -r requirements/local.txt
    
    
Then simply apply the migrations:

    $ python manage.py migrate
    

You can now run the development server:

    $ python manage.py runserver

#### Run celery worker (On windows only )
  $` celery -A Gimsap  worker -l info --pool=solo`

### Test server for email (On Powershell only)
` try{
     Send-MailMessage -from gimsap@zerotozenithmedia.com -to codertjay@gmail.com -Subject "Test OK" -Body "Test is OK" -SmtpServer zerotozenithmedia.com
    }
 catch{
     Send-MailMessage -from gimsap@zerotozenithmedia.com -to codertjay@gmail.com -Subject "Test OK" -Body "Test is OK" -SmtpServer zerotozenithmedia.com
 }`