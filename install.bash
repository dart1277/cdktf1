#!/bin/bash
# https://dev.to/aws-builders/cdk-for-terraform-cdktf-on-aws-how-to-configure-an-s3-remote-backend-and-deploy-a-lambda-function-url-using-python-3okk


nvm install --lts
nvm alias default v20.11.1
npm init
sudo apt install terraform
sudo terraform -install-autocomplete
npm install --global cdktf-cli@latest
alias terraform=tf
pip install pipenv
mkdir -p s3_be
cd s3_be
# When you use npm install to install a pre-built provider, 
# you should not define that provider again in your cdktf.json file.
# If you receive errors while running cdktf synth because of duplicate providers,
# remove the duplicates from your cdktf.json file, delete tsbuildinfo.json, and run cdktf synth again.
# npm install -g @cdktf/provider-aws
pipenv install cdktf-cdktf-provider-aws
pipenv install python-dotenv
pipenv install python-dotenv[cli]

# default plugin cache:
# TF_PLUGIN_CACHE_DIR=$HOME/.terraform.d/plugin-cache
# or use .terraformrc config file to configure

# ~> allows only "rightmost version upgrade"
# if you don't want to use remote state add  --local flag to command below
cdktf init --template="python" --providers="aws@~>5.38"

pipenv shell

# get provider
cdktf get
cdktf synth
cdktf plan
cdktf deploy


# local state migration
cd cdktf.out/stacks/first_project
terraform init --migrate-state

dotenv -f dotenv/.env-dev run -- cdktf deploy --auto-approve
dotenv -f dotenv/.env-dev run -- cdktf deploy --auto-approve --var="tfMsg=hello cmdline"


# terraform reconfiguration

cd cdktf.out/stacks/main_stack_construct

│ If you wish to attempt automatic migration of the state, use "terraform init -migrate-state"
│ If you wish to store the current configuration with no changes to the state,
│ use "terraform init -reconfigure".
