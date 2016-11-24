#!/usr/bin/env bash
cd src
zip -r ../artifact *
cd ..
curl -F artifact=@./artifact.zip -F project=$MOLLY_PROJECT -F token=$MOLLY_TOKEN $MOLLY_URL"/deploy"
