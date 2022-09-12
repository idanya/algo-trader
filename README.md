# algo-trader


### Running locally
algo-trader is using MongoDB for data storage. In order to run Mongo locally use `docker-compose`.
```shell
docker-compose -f docker-compose.yml up -d
```

### Running tests
* Unit: `./scripts/test-unit.sh`
* Integration (needs IB gateway running): `./scripts/test-integration.sh`
* All: `./scripts/test-all.sh`

