#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

APP_NAME="aqua-rex4"


# Define the branch to deploy (default is "main")
BRANCH=${1:-DEV}

deploy_to_heroku() {
    local APP_NAME=$1
    echo "Deploying to Heroku app: $APP_NAME"

    # Add Heroku remote if not already added
    if ! git remote | grep -q $APP_NAME; then
        echo "Adding remote for $APP_NAME"
        heroku git:remote -a $APP_NAME -r $APP_NAME
    fi

    # Push the branch to the Heroku remote
    echo "Pushing $BRANCH branch to Heroku app: $APP_NAME"
    git push $APP_NAME $BRANCH:main --force

    # Add Node.js buildpack
    # echo "Adding Node.js buildpack to $APP_NAME"
    # heroku buildpacks:add --app $APP_NAME heroku/nodejs

    # Ensure a Postgres addon exists
    echo "Ensuring Postgres addon exists for $APP_NAME"
    heroku addons:create heroku-postgresql:essential-0 --app $APP_NAME || echo "Postgres addon already exists"

    # Check environment variables, make sure the database line has postgres 
    echo "Fetching environment variables for $APP_NAME"
    heroku run "env" --app $APP_NAME

    # Check settings differences
    echo "Running diffsettings for $APP_NAME"
    heroku run "python3 manage.py diffsettings" --app $APP_NAME

    # Run makemigrations
    echo "Running makemigrations for $APP_NAME"
    heroku run "python3 manage.py makemigrations" --app $APP_NAME

    # Run migrations
    echo "Running migrations for $APP_NAME"
    heroku run "python3 manage.py migrate" --app $APP_NAME

    # Scale the Worker
    echo "Scale the Worker"
    heroku ps:scale worker=1 --app $APP_NAME

}

deploy_to_heroku $APP_NAME
echo "Deployment to both Heroku apps completed successfully!"