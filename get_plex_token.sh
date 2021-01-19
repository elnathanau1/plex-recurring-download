#!/bin/sh

read -p 'plex.tv Username: ' uservar
echo ''
read -sp 'plex.tv Password: ' passvar

url="https://plex.tv/api/v2/users/signin?login=$uservar&password=$passvar&X-Plex-Client-Identifier=12345abcDEF"
response=$(curl -X POST -i -k -L -s $url)
# Grap the token
UserToken=$(printf %s "$response" | awk -F= '$1=="authToken"{print $2}' RS=' '| cut -d '"' -f 2)

echo "************************* Token *******************************************"
echo $UserToken
echo "***************************************************************************"

