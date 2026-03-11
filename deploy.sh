pip#!/bin/bash

docker compose up -d

cd ../../../terraform
terraform apply --auto-approve

cd ../layers/twilio/python
rm -rf aio** attr** bin cert** charset** frozen** idna** jwt multidict** propcache** pyjwt** requests** twilio** typing_extensions** urllib3** yarl** **.pyd

cd ../../../
docker compose down