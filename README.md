# Loc Nguyen - Assignment for BlockSwap

## Description

### Purpose

Pull GraphQL & QuickNode data to get & store validator sweeps into PostgreSQL for further analysis.

### Expected Result

```
blockswap-worker-1         | [2023-04-10 18:29:07,707: WARNING/ForkPoolWorker-16] Total balance: 3139475271265
```

## Architecture & usage

### Commands

- Make a `.env` file according to `.env-template` (especially with QuickNode & The Graph API vars)
- Run `docker compose up` to start the worker and the database
- Every 30 seconds, the worker will pull data from QuickNode & The Graph API, and store it into the database
- Every 90 seconds, the worker will calculate the total balance of all validators & print out in log
- Monitor the tasks at `http://localhost:5555`

### Architecture

The Graph > QuickNode > Celery (on Redis) > PostgreSQL.

#### Celery

Celery is selected for its lightweightedness, and its ability to run tasks in the background with minimal overhead & latency.

#### PostgreSQL

PostgreSQL is selected for its ease of use, and its ability to store JSON data. Its selection is representative & can be replaced by a more performant database such as TimescaleDB or Druid.

### Challenges & Next steps

- [ ] Verify that business logic is correct
- [ ] Verify that data is correct & complete
- [ ] Add user friendly visualizations
- [ ] Log balances results to database
- [ ] Better data modelling

### Contact

- Email: vinhloc30796@gmail.com