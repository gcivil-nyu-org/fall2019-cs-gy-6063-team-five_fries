# Team FiveFries Project Repository (NYCityStreet)

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


### To Set up Project

#### Getting Google API Key

In order to authenticate with Google's Places API, which is necessary to utilize the Geocoding and Reverse Geocoding endpoints, a Project and Billing Account must be created with Google, and the API enabled on it.

A Billing Account requires a valid credit card to be attached to it in order to work.  Luckily, the free API tier Google offers is generous enough that you should never worry about having to pay for the API usage, although pricing details can be found [here](https://cloud.google.com/maps-platform/pricing/).  

To get started with the Google API platform, instructions for creating a Billing Account can be found [here](https://developers.google.com/maps/gmp-get-started).

When starting, insure that you enable your account for the Places APIs, which includes the Geocoding API that we will primarily be using. You will be prompted to select or create a project to associate your API key and billing account with. If you already have an existing one that you would like to use, select that. If not, go ahead and create a new project.

Once the project is created, you will be prompted to create or add a Billing Account to your profile.  Once your project has an associated Billing Account, an API key should be generated to authenticate your requests. It can be found under the Credentials section of the APIs & Services tab. Copy this key into your heroku app's Config Vars with the key name `GOOGLE_API_KEY`.  This will allow your app to authenticate and retrieve Google Geocode API results.

#### Getting Zillow API Key

See instructions here [https://www.zillow.com/howto/api/APIOverview.htm](https://www.zillow.com/howto/api/APIOverview.htm)

#### Getting NYC OpenData 311 API Key

#### Email Account Authentication

This project uses email authentication via django-allauth to confirm user accounts and for password resets.  Currently the project is configured just to use simple username/password credentials with a gmail account in order to send the emails.  

To configure your own gmail account the send out emails for the project, simply create a new google account to be used as the sender.  Once that is done, you will need to turn on Less Secury App access in the account, otherwise it will refuse the email/password combo that is specified in settings.py.  

To do this, log into your email google account and navigate to [https://myaccount.google.com](https://myaccount.google.com) and click on the Security menu item on the left hand side.  In the Security menu, scroll down until you reach the Less Secure App access setting. Turn this on.

Once this is done, navigate to the settings.py file in the `citystreets/` folder of your project directory.  Scroll down until you reach the `# Emails information` section, and replace the values for `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` with the gmail address and login password.  Save `settings.py` and you should be good to go for email authentication and password reset.


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
