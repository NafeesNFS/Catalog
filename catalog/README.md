## Item-Catalog-Udacity
By Nafees Akhtar
This web application is a project for the Udacity Full Stack Nano Degree.


## About

This project is a  web application which utilizes the Flask Framework and uses SQL database to insert the tables and their values into the database. In this project you can find Websites and their corresponding tools or it may be any website introduced by the above website.


## In This Project

This project has one main Python module `web_main.py` which runs the Flask application. A SQL database is created using the `Webdb_Setup.py` module and you can populate the database with test data using `webdb_init.py`.
The Flask application uses stored HTML templates in the tempaltes folder to build the front-end of the application.


## Skills Required

1. Python
2. HTML
3. CSS
4. OAuth
5. Flask Framework
6. DataBaseModels


## In This Project Main files

   1.In this project contains web_main.py contains routes and json endpoints.
   2.webdb_setup.py contains the database models and tablenames it creates a database file with table.
   3.webdb_init.py contains the sample data and insert into the database.
   
   
## Features

1. Checking the Proper authentication and authorisation.
2. Full CRUD support using Flask and SQLAlchemy.
3. Using the JSON endpoints.
4. Implements oAuth using with Google Sign-in API.


## Tips to Run Project

1. Set up a Google Plus auth application.
2. go to google and login with Google.
3. Create a new project
4. Select "API's and Auth-> Credentials-> Create a new OAuth client ID" from the project menu
5. Select Web Application
6. follow the tips given by google


## How to install and run the project:

1.  Download  Vagrant and then install  it.

2. Download  VirtualBox and then install it.

3. Clone or download the Vagrant VM configuration file from here.

4. Open the above directory and navigate to the vagrant/ sub-directory.

5. Open terminal, and type

6. vagrant up
  This will cause Vagrant to download the Ubuntu operating system and install it. This may take quite a while depending on how fast your Internet connection is.

  After the above command succeeds, connect to the newly created VM by typing the following command:

7. vagrant ssh
  Type cd /vagrant/ to navigate to the shared repository.

8. Download or clone this repository, and navigate to it.

9. Install or upgrade Flask:

10. sudo python -m pip install --upgrade flask
    Run the following command to set up the database:

11. python webdb_setup.py
    Run the following command to insert dummy values. If you don't run this, the application will not run.

12. python webdb_init.py
    Run this application:

13. python web_main.py
Open http://localhost:8000/ in your Chrome browser and then you can find the websites and their tools.

14. Debugging
    In case the app doesn't run, make sure to confirm the following points:

15. You have run python webdb_init.py before running the application. This is an essential step.

16. The latest version of Flask is installed.

17. The latest version of Python is installed.


## JSON Endpoints
The following are open to the public which displays the code:

Websites Catalog JSON: `/WebsiteHub/JSON`
    - Displays the whole websites tools catalog. Website Categories and all tools.

Website Categories JSON: `/websiteHub/websiteName/JSON`
    - Displays all Website categories
	
All Website Editions: `/WebsiteHub/website/JSON`
	- Displays all Website Tools

Website Edition JSON: `/WebsiteHub/<path:websitename>/website/JSON`
    - Displays Website tools for a specific Website category

Website Category Edition JSON: `/WebsiteHub/<path:websitename>/<path:websitetool_name>/JSON`
    - Displays a specific Website tool category Model.