#!/usr/bin/env bash

# how to start dynamodb
cd ~/dynamodb
java -Djava.library.path=~/dynamodb/DynamoDBLocal_lib -jar ~/dynamodb/DynamoDBLocal.jar -sharedDb &
exit 0
