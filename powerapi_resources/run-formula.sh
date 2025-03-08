docker run -t \
--net=host \
-v $(pwd)/config-formula.json:/config-formula.json \
powerapi/smartwatts-formula --config-file /config-formula.json
