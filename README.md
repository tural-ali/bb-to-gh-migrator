# bb-to-gh-migrator
A small handy tool to move ALL repositories from Bitbucket to Github


# What it does

 - Get all repos in BitBucket (and loop thought them)
 - Create a new repo on GitHub with the same slug name (ensures there isn't already one with the same name)
 - Does a bare clone of the BB repo and mirros it to GH
 
 
# Prerequisites

 - Fast internet speed
 - pipenv and python installed environment
 
 # Setup

! To run the script you should update the following variables, which can be found on top of the script:

```
APP_KEYS: A map containing the keys to authenticate on BB and GH.
BB_USER: Your username on BitBucket
GH_USER: Your username on GitHub
BB_EMAIL: The email which will be used to identify your client against the BitBucket API.
```
Also copy you `less ~/.ssh/id_rsa.pub` output to both your Github and Bitbucket account's ssh key settings. If it doesn't output anything, create one like this `ssh-keygen` and press enter every time until it generates the files.

  - Clone this repository
  - If you're using Ubuntu or Debian run `apt install python-pip`, if MacOSX run `brew install pipenv`
  - Edit the migrate.py according to the instructions above
  - Create folder for the migration files `cd ~ && mkdir git && mkdir git/bitbucket-migration`
  - Navigate to the application's directory and run `pipenv install`, it will install all needed libraries and modules
  - Run `pipenv shell`
  - Run `python ./migrate.py`
  
