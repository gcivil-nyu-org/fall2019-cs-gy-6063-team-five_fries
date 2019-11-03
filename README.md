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

In order to authenticate with Google's Places API, which is necessary to utilize the Geocoding and Reverse Geocoding endpoints, an Project and Billing Account must be created with Google, and the API enabled on it.

A Billing Account requires a valid credit card to be attached to it in order to work.  Luckily, the free API tier Google offers is generous enough that you should never worry about having to pay for the API usage, although pricing details can be found [here](https://cloud.google.com/maps-platform/pricing/).  

To get start with the Google API platform, instructions for creating a Billing Account can be found [here](https://developers.google.com/maps/gmp-get-started).

When starting, insure that you enable your account for the Places APIs, which includes the Geocoding API that we will primarily be using. You will be prompted to select or create a project to associate your API key and billing account with. If you already have an existing one that you would like to use, select that. If not, go ahead and create a new project.

Once the project is created, you will be prompted to create or add a Billing Account to your profile.  Once your project has an associated Billing Account, an API key should be created to authenticate your requests. It can be found under the Credentials section of the APIs & Services tab. Copy this key into your heroku app's Config Vars with the key name `GOOGLE_API_KEY`.  This will allow your app to authenticate and retrieve Google Geocode API results.
