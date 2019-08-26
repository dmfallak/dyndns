#!/bin/bash

a=`echo $(upnpc -s | grep ExternalIPAddress | cut -d " " -f 3)`
b=`echo $(dig +short hostto.update.com)`

if [ "$a" != "$b" ]; then
  # public ip has changed, update the dns record
  curl -s -X POST -H "x-api-key: hihih" "https://je8opgvagd.execute-api.us-east-1.amazonaws.com/prod/" >/dev/null
fi
