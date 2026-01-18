## Frontend Setup

## Prerequisites

- npm --version >=10.1.0
- node --version >=v20.9.0

## Backend should be running on http://localhost:8000 or if running on another port then change REACT_APP_API_BASE_URL value in .env

cd Frontend/consuma_ai

## install packages

- npm i

## run the server

- npm start

###############################################################################
###############################################################################
###############################################################################

## Backend Setup

## PreRequisites

- python3 version >= 3.10
- docker

## Setting up Backend

- cd Backend (Move to the directory)

## Run below commands to get MySQL DB container and verify whether mysql:8.0 container is in running state

- docker compose up -d
- docker ps

##Create a virtual env and Activate the env

- python3 -m venv venv
- source venv/bin/activate

## Verify the python, it should point to Backend/venv/bin/python

- which python

## Upgrade pip and install packages

- pip install --upgrade pip
- pip install .

## Upgrade db schema

- alembic upgrade head

## Set the below env variable to run cron for scheduling failed_callbacks only on one worker

export RUN_SCHEDULER=true

## Run the server

Note: If starting server on new terminal, then first set env variable using export RUN_SCHEDULER=true

- uvicorn app.main:app --workers 4 (Run the server)
  (Taken into consideration that the minimum no of cores in the running machine are 8)

###############################################################################
###############################################################################
###############################################################################

## How to use Functionalities

Run the Backend Server and endpoints with payload to be provided can seen from http://localhost:8000/docs

## run load generator script

- cd Backend (in venev)

## sync request storm

- python3 app/scripts/load_generator.py sync (generates file with name sync_report.txt that provides p50,p95 and p99 statistics)

## async request storm

- python3 app/scripts/load_generator.py async <callback_url> (generates file with name async_report.txt that provides success and failure report but the actual time of callback completion can be seen only from the requests table for async i.e Request Details by Mode)

###############################################################################
###############################################################################
###############################################################################

## Design Decisions

- Deterministic work instead of Side Effects.
  The core business logic is implemented as deterministic functions, meaning the same input always produces the same output. This makes the system easier to test, reason about, and debug.
  This design choice was made specifically to support CPU-intensive workloads without blocking the event loop. By keeping the core logic free of side effects (such as direct database writes or network calls), the computation can be safely offloaded to background execution (e.g., a ProcessPoolExecutor). This ensures the FastAPI event loop remains responsive, improving throughput, predictability, and overall system stability while simplifying error handling and retries.

  ###

- Use of ProcessPoolExecutor for the deterministic work.
  CPU-bound deterministic work is offloaded to a ProcessPoolExecutor instead of running in the event loop. This prevents blocking the FastAPI event loop and allows true parallel execution by bypassing Python’s GIL, improving throughput and keeping the API responsive under load.

  ####

- Starting server with 4 workers to have more event loops.
  The server is started with 4 workers to leverage multi-core CPUs, with each worker running its own event loop. This allows the application to handle more concurrent requests efficiently while improving overall availability and fault isolation.
  Note: The combination of server workers and the ProcessPoolExecutor size must always be carefully fine-tuned based on the number of CPU cores available and the nature of the workload. In the current design, this configuration was chosen with an 8-core CPU in mind, balancing event-loop concurrency with parallel execution of CPU-bound deterministic tasks to avoid over-subscription and context-switching overhead.

  ###

- Lifespan usage for shared states.
  FastAPI’s lifespan events are used to initialize and clean up shared application state. This ensures that expensive or critical resources (such as executors or configuration objects) are created once per worker at startup and properly released during shutdown, leading to predictable lifecycle management.

  ###

- Configuration loading in shared state.
  Application configuration is loaded during the lifespan startup phase and stored in shared state. This avoids repeated configuration reads per request, ensures consistency across requests within a worker, and centralizes configuration management.

  ###

- callback with retry mechanism for async workers.
  For async requests, results are delivered via a callback mechanism with a retry strategy. This improves reliability when downstream systems are temporarily unavailable by automatically retrying failed callbacks, reducing data loss and increasing robustness in distributed environments.

- cron job for failed async callbacks
  A scheduled cron job runs every 10 minutes to retry and complete failed async callbacks. This acts as a safety net for cases where callbacks fail due to transient issues such as network errors or temporary downstream unavailability. By decoupling retries from request handling, this approach improves reliability, ensures eventual delivery, and prevents retry logic from impacting request latency or event loop responsiveness.

### Architecture Design

```text
                         ┌─────────────────────────┐
                         │        Clients          │
                         └────────────┬────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────┐
                        │       OS Kernel (TCP)    │
                         │  accept() scheduling
                        └────────────┬─────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐┌──────────────────────────┐
         │                           │                           │                           │
         ▼                           ▼                           ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐.        ┌─────────────────┐
│ UVicorn Worker 1 │       │ UVicorn Worker 2 │       │ UVicorn Worker 3 │        │ UVicorn Worker 4 │
│ (Event Loop)     │       │ (Event Loop)     │       │ (Event Loop)     │        |   (Event Loop)   |
└────────┬────────┘       └────────┬────────┘       └────────┬────────┘          └────────┬────────┘
         │                           │                           │                        |
         │  Sync / Async Handlers    │  Sync / Async Handlers    │ Sync / Async Handlers  |
         │  (Non-blocking)           │  (Non-blocking)           │  (Non-blocking)        |
         │                           │                           │                        |
         ▼                           ▼                           ▼                        ▼
 ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐  ┌─────────────────────┐
 │ ProcessPoolExecutor │     │ ProcessPoolExecutor │     │ ProcessPoolExecutor │    ProcessPoolExecutor
 │ max_workers = 2     │     │ max_workers = 2     │     │ max_workers = 2     │     max_workers = 2
 └───────┬───────┬─────┘     └───────┬───────┬─────┘     └───────┬───────┬─────┘  └───────┬───────┬─────┘
         │       │                   │       │                   │       │                |       |
         ▼       ▼                   ▼       ▼                   ▼       ▼                ▼       ▼
   CPU Process  CPU Process     CPU Process  Async API call     CPU Process  CPU Process. CPU Process CPU Process
   (Task Exec)  (Task Exec)     (Task Exec)      |              (Task Exec)  (Task Exec)  (Task Exec) (Task Exec)
                                                 ▼
                                            http to Callback with retries
                                                 |
                                                 ▼
                                              DataBase (state saved in database)


Callback Cron (Every 10 mins)
 ┌─────────────────────┐
 │     Database        │
 │    │
 └───────┬───────┬─────┘
         │
       Scheduler (fetch from database where mode='async' and status='callback_failed' )  and run them
```

Note: This design must always be tuned based on the available machine resources (CPU cores, memory, and workload characteristics) of the environment in which it is running.

What we achieved?

- Efficient parallel execution without event-loop starvation
  The system cleanly separates I/O-bound and CPU-bound workloads by leveraging asynchronous I/O for request handling and process-based execution for compute-intensive tasks. This ensures high concurrency while preserving event loop responsiveness and predictable latency under load.

- Robust asynchronous callback delivery with retry guarantees
  Async operations are decoupled from client interaction using a callback-based completion model. Callback failures are detected, persisted, and retried in a controlled manner, providing eventual delivery guarantees while preventing failure amplification or retry storms.

- Scheduled retry orchestration for failed callbacks
  A time-based retry mechanism (cron-driven) periodically scans for failed async callbacks and attempts redelivery. This design ensures resilience against transient downstream outages, survives service restarts, and enforces bounded retries without blocking application resources.

- Budget Friendly robust system

### Trade offs

- In-process scheduler vs distributed scheduling

  Current choice
  Cron-style scheduler running within the service
  Simple, predictable, easy to reason about

  Trade-off
  Not horizontally scalable by default

  Possible improvements
  Move retries to a queue-based delayed retry system ( Kafka / Redis)

- Bounded retries without Dead Letter Queue (DLQ)

  Current choice
  Fixed retry attempts
  Mark as failed after limit

  Trade-off
  Failed callbacks require manual inspection
  Cron job running on a single process to replay the callbacks

  Possible improvement
  Introduce a DLQ (dead-letter state/table/topic)
  Enable manual or automated replay in a separate service

- Single-tier retry policy

  Current choice
  Uniform retry interval (every 10 minutes)

  Trade-off
  Not adaptive to different failure types
  Slower recovery for transient failures

  Possible improvement
  Exponential backoff with jitter
  Error-class-based retry strategy (4xx vs 5xx)

- Database as both state store and coordination mechanism

  Current choice
  DB tracks job state and retries
  Simple and durable

  Trade-off
  DB can become a bottleneck at high scale
  Polling introduces periodic load

  Possible improvement
  Split responsibilities:
  a. DB for durability
  b. Queue for scheduling and execution
