# Team FiveFries Project Repository (NYCityStreet)

## Build Status

[![Build Status](https://travis-ci.com/gcivil-nyu-org/fall2019-cs-gy-6063-team-five_fries.svg?token=SEGpBz7LdWjrjw6AhUsE&branch=master)](https://travis-ci.com/gcivil-nyu-org/fall2019-cs-gy-6063-team-five_fries)
[![Coverage Status](https://coveralls.io/repos/github/gcivil-nyu-org/fall2019-cs-gy-6063-team-five_fries/badge.svg?branch=master&service=github)](https://coveralls.io/github/gcivil-nyu-org/fall2019-cs-gy-6063-team-five_fries?branch=master)

## Heroku instance
- [production](http://master-branch.herokuapp.com/)
- [integration](https://develop-branch.herokuapp.com)


## Set up
### Environment variables
- `ZWSID`: Zillow API key
- `KEY_311`: NYC 311 dataset token
- `COVERALLS_REPO_TOKEN`: Coveralls token (set this variable on travis)
- `GOOGLE_API_KEY`: API Key used to authenticate with Google's Places API
- `REDIS_URL`: URL that tells your Project's built in Celery worker where to connect to Redis


### To Set up Project

#### Getting Google API Key

In order to authenticate with Google's Places API, which is necessary to utilize the Geocoding and Reverse Geocoding endpoints, a Project and Billing Account must be created with Google, and the API enabled on it.

A Billing Account requires a valid credit card to be attached to it in order to work.  Luckily, the free API tier Google offers is generous enough that you should never worry about having to pay for the API usage, although pricing details can be found [here](https://cloud.google.com/maps-platform/pricing/).  

If this is your first time signing up for a Google Billing account, you are automatically granted a $300 credit. This credit translates into 60,000 Geocode API requests, and even better your requests don't start counting against it until after you've used up the current month's free tier requests.
As of right now (2019/12/10) the free tier for the Geocode API is $200, or 40,000 requests. 

Please note though, that different API's have different price points, so if another Google API is integrated into the project using the same billing account it may reduce the total number of requests made in a given month that qualify as free.  

To get started with the Google API platform, instructions for creating a Billing Account can be found [here](https://developers.google.com/maps/gmp-get-started).

When starting, insure that you enable your account for the Places APIs, which includes the Geocoding API that we will primarily be using. You will be prompted to select or create a project to associate your API key and billing account with. If you already have an existing one that you would like to use, select that. If not, go ahead and create a new project.

Once the project is created, you will be prompted to create or add a Billing Account to your profile.  Once your project has an associated Billing Account, an API key should be generated to authenticate your requests. It can be found under the Credentials section of the APIs & Services tab. Copy this key into your heroku app's Config Vars with the key name `GOOGLE_API_KEY`.  This will allow your app to authenticate and retrieve Google Geocode API results.

#### Getting Zillow API Key

See instructions here [https://www.zillow.com/howto/api/APIOverview.htm](https://www.zillow.com/howto/api/APIOverview.htm)

#### Getting NYC OpenData 311 API Key

Get started by creating an account here [https://opendata.socrata.com/login](https://opendata.socrata.com/login)

#### Email Account Authentication

This project uses email authentication via django-allauth to confirm user accounts and for password resets.  Currently the project is configured just to use simple username/password credentials with a Gmail account in order to send the emails.  

To configure your own Gmail account the send out emails for the project, simply create a new google account to be used as the sender.  Once that is done, you will need to turn on Less Secure App access in the account, otherwise it will refuse the email/password combo that is specified in `settings.py`.  

To do this, log into your email google account and navigate to [https://myaccount.google.com](https://myaccount.google.com) and click on the Security menu item on the left hand side.  In the Security menu, scroll down until you reach the Less Secure App access setting. Turn this on.

Once this is done, navigate to the `settings.py` file in the `citystreets/` folder of your project directory.  Scroll down until you reach the `# Emails information` section, and replace the values for `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` with the gmail address and login password.  Save `settings.py` and you should be good to go for email authentication and password reset.


### Local Project setup

#### MacOS Project Setup

##### Install Python 3
Although Python 2 is installed by default on most Macs, Python 3 is required for this project. Confirm the installed version of python by opening the Terminal and typing `python --version`. To check to see if Python3 is already installed type `python3 --version` in the terminal and hit enter.  

##### Install Xcode and Homebrew
We will use the package manager Homebrew to install Python3. Homebrew depends on Apple's Xcode package, so install Xcode through the AppStore or by running the following command in the Terminal.
`xcode-select --install`

Next, install Homebrew by pasting the following into the terminal and hitting Enter, or by following the instructions here: [http://osxdaily.com/2018/03/07/how-install-homebrew-mac-os/](http://osxdaily.com/2018/03/07/how-install-homebrew-mac-os/):
`/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

Finally, install the latest version of Python by running the following command: `brew install python3`

Confirm that it was installed correctly: `python3 --version`. You should see `Python 3.X.X` output in the terminal.

##### Install pip and virtualenv

pip is the preferred way to install dependencies, including Django.  Documentation for installing pip can be found [here](https://pip.pypa.io/en/stable/installing/).  Once pip is installed, it is trivial to install the virtualenv package (for isolating project dependencies).  If your Python version is creater than 3.3, then `virtualenv` comes installed along with by default.  Otherwise, in the Terminal type `pip install virtualenv`.  

Once virtualenv has been installed, navigate to the cloned project directory and create a local virtualenv folder with `virtualenv venv`.  If virtualenv is included in your Python installation, then the command is `python3 -m venv venv`. This will create a folder in you project directory called `venv/` which will store your local project dependencies.  Activate you virtual environment by typing `source venv/bin/activate`, and install your local dependencies in the virtual environment by typing `pip install -r requirements.txt`, which will download and install all the project required software listed in the `requirements.txt` file that was cloned with the project. The virtual environment can be turned off anytime by typing `deactivate` in the Terminal in the project base directory.

On some versions of MacOS, the dependencies installation process may be interrupted by a failure to install the dependency `psycopg`. If that happens and dependency installation is aborted, run `pip install psycopg2==2.7.5`, and then run `pip install -r requirements.txt` again.



### Testing/Local run instructions for Celery/Redis

#### Heroku Setup

Please see the instructions here: [https://devcenter.heroku.com/articles/celery-heroku#running-locally](https://devcenter.heroku.com/articles/celery-heroku#running-locally)


#### For Local Testing

Firstly, to run the celery/redis data worker locally there are a couple of dependencies to install.

The `Redis` components can be installed easily via `HomeBrew` on MacOS.  Merely type in `brew install redis`.
Once Redis has been installed, the local redis URL must be added to the system variables. Run `export REDIS_URL=redis://localhost`.


Open up 3 separate terminal windows. In one start up the Django local server, `python manage.py runserver`. In the second one start up the redis server, `redis-server`. And finally start up the Celery worker, `celery -A citystreets.celery worker`.

Now you are able to test/run the Celery worker.

To view the logs on heroku, run: `heroku logs --tail --app APP_NAME --dyno worker`.

Some sample queries to kick off the worker

- Small Query

`{host}/refresh_apartment/?city=bk&limit=10`

- Larger query (may take over an hour to complete)

`{host}/refresh_apartment/?city=brx,brk,fct,lgi,mnh,jsy,que,stn,wch&limit=1000`

Please note that very large queries may result in a large number of requests made against the Geocode API, so it pays
to be mindful to not go over the API's free limits.

## First Steps!

### Account Creation

We encourage everyone to create their own (or multiple!) user accounts for testing day.  The telephone field is no longer mandatory
(unless you feel like it) and we have removed the restriction on different account types; so any one particular account can be a Tenant, Renter, and/or a Landlord.  Please make sure to sign up with a valid email address that you have access to as you will not be 
able to log in until you have confirmed your account via email.  All emails for account activation and password resets (done from the login page) will be sent out from `team.five.fries@gmail.com`.

For test day, we encourage everyon to test out the limits of our search functionality to see where it breaks. We have pulled in a large number of apartment locations from our data sources so there should be plenty for people to find.  Unfortunately though the APIs that are accessible to us do not provide images for locations, so other than those that are user uploaded most apartments will not have a locally stored picture.

We also encourage everyone to test the functionality surrounding apartment uploading, editing, favoriting, and reviewing. What happens when you try to upload multiple apartments to the same place, or when a location has a ton of reviews, or when multiple users try to claim to be the landlord for a building? Let us know!

### A generic user interaction flow.

1. Sign Up for an account (you need 2 accounts to test the entire functionality).
2. Login
3. Search for a location (e.g. based on street address, zipcode etc.). Searching based on zipcode should also display general complaint levels for that zipcode.
4. The search page displays different locations along with the number of apartments at each location that satisfy your selected criteria. Click on a particular location to see all the apartments at that location. You can also display them on a map to get a better idea of the neighborhood.
5. You can favorite a particular location and then go to the "Favorites" tab on the navigation bar to see your favorites list. You can remove an apartment from favorites as well.
6. You can also leave a review for a particular location and it should display in your account page (accessible from "My account" on the navigation bar) and under that location's reviews. In order to leave a review, you need to set yourself as a tenant of one of the apartments at that location. You can do this by clicking on the "Are you a tenant or landlord.....?" in the apartment detail view.
7. Next, try to upload your apartment. You can find this apartment under your account view.
8. Next, try to search for some location and go to some apartment inside that location, setting yourself as the landlord (by clicking on the "Are you a tenant or landlord.....?"). For now, it does not do any validation and automatically sets you up as the tenant/landlord.
9. In order to be able to contact the landlord for an apartment that you are interested in, you can find an apartment that already has a landlord. However, this might not be easy to find since most of our data is coming from Craigslist and Zillow and we don't have the landlords for those apartments set up. Since we don't allow the landlord to contact the landlord (himself/herself), you would need to logout and login from the other account that you created in order to send the landlord a message by going to the apartment view and clicking on the "Interested?" button.

