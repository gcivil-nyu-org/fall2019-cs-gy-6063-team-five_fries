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


### Local Project setup

#### MacOS Project Setup

##### Install Python 3
Although Python 2 is installed by default on most Macs, Python 3 is required for this project. Confirm the installed version of python by opening the Terminal and typing `python --version`. To check to see if Python3 is already installed type `python3 --version` in the terminal and hit enter.  

##### Install Xcode and Homebrew
We will use the package manager Homebrew to install Python3. Homebrew depends on Apple's Xcode package, so install Xcode through the AppStore or by running the following command in the Terminal.
`xcode-select --install`

Next, install Homebrew by pasting the following into the terminal and hitting Enter:
`/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

Finally, install the latest version of Python by running the following command: `brew install python3`

Confirm that it was installed correctly: `python3 --version`. You should see `Python 3.X.X` output in the terminal.

##### Install pip and virtualenv

pip is the preferred way to install dependencies, including Django.  Documentation for installing pip can be found [here](https://pip.pypa.io/en/stable/installing/).  Once pip is installed, it is trivial to install the virtualenv package (for isolating project dependencies).  In the Terminal type `pip install virtualenv`.  

Once virtualenv has been installed, navigate to the cloned project directory and create a local virtualenv folder with `virtualenv venv`. This will create a folder in you project directory called `venv/` which will store your local project dependencies.  Activate you virtual environment by typing `source venv/bin/activate`, and install your local dependencies in the virtual environment by typing `pip install -r requirements.txt`, which will download and install all the project required software listed in the `requirements.txt` file that was cloned with the project.
