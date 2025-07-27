# Distributed Text Analyzer

## Objective

Set up a distributed system capable of:

* Efficiently consuming a high volume of RabbitMQ messages.
* Processing each message with a heavy business task (text analysis).
* Storing results in MongoDB.
* Emitting a final message once processing is complete.
* Testing load with a simulator.

## Tech Stack

| Component            | Role                                                        |
|----------------------|-------------------------------------------------------------|
| **RabbitMQ**         | AMQP message broker for message ingestion                   |
| **aio-pika**         | Asynchronous Python client for RabbitMQ                     |
| **MongoDB**          | NoSQL database for storing results                          |
| **motor**            | Asynchronous MongoDB client for Python                      |
| **Docker Compose**   | Local orchestration of all services                         |
| **loadgen**          | Message generator for testing                               |

---

## Technical Choices Justification

### Why `aio-pika`?

* Asynchronous AMQP client: ideal for `asyncio` systems
* Enables non-blocking RabbitMQ message consumption
* Simpler and more modern than synchronous `pika`
* Easier to scale in an event-loop-based architecture
* Handles reconnects, QoS, explicit acks, publishing, etc.
* Compatible with asynchronous processing + ProcessPoolExecutor

### Why `motor`?

* Official asynchronous MongoDB driver
* Perfect for inserting/updating documents without blocking
* Integrates natively with `asyncio`, compatible with `aio-pika`
* More performant than `pymongo` in concurrent applications

These two choices allow efficient continuous message processing, scale well, and avoid **unnecessary** event loop blocking.

### Why `asyncio` + `ProcessPoolExecutor`?

* `asyncio` efficiently orchestrates continuous message flow and I/O operations (MongoDB, RabbitMQ) without blocking
* Ideal for reactive, event-driven architectures with low thread consumption
* `ProcessPoolExecutor` allows running **CPU-bound** tasks in parallel (e.g., scoring, NLP, parsing)
* Best of both worlds: non-blocking reactivity + parallel computation power
* Decouples heavy business logic from main flow without hurting overall performance

This architecture efficiently handles a high-throughput RabbitMQ message stream while processing heavy business logic in parallel.

* `asyncio` handles non-blocking operations: RabbitMQ consumption, MongoDB insertion, publishing, etc.
* CPU-intensive tasks are offloaded to worker processes via `ProcessPoolExecutor`, freeing the main event loop.

![Architecture asyncio + ProcessPoolExecutor](./assets/Parallel_processing.png)

---

## Project Modules

### 1. `worker/` — Main analysis service

* `aio-pika` for RabbitMQ consumption
* `motor` for MongoDB persistence
* `ProcessPoolExecutor` for CPU-bound processing
* Publishes processed message to `processed_texts` queue

### 2. `loadgen/` — Load simulator

* Generates a massive volume of `update` or `delete` messages

---

## Project Structure

```bash
project/
├── assets/                         # Images (diagrams, docs, etc.)
│   └── Parallel_processing.png

├── docker-compose.yml              # Service orchestration (RabbitMQ, MongoDB, etc.)
├── .gitignore                      # Git-ignored files and folders
├── pyproject.toml                  # Config for black and isort
├── Makefile                        # Useful commands

├── worker/                         # Main text analysis service
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── setup.py
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── requirements-test.txt

│   ├── app/                        # Business logic
│   │   ├── consumer.py
│   │   ├── main.py
│   │   ├── processing.py
│   │   ├── publisher.py
│   │   ├── storage.py
│   │   └── models/
│   │       └── message_data.py

│   └── core/                       # Utility tools
│       └── logging_wrapper.py

│   └── tests/                      # Unit tests
│       └── test_delete_process.py
│       └── test_message_data.py
│       └── test_message_data_errors.py
│       └── test_processing.py
│       └── test_publisher.py
│       └── test_update_process.py

├── loadgen/                        # RabbitMQ load generator
│   ├── main.py
│   ├── config.yaml
│   └── ...

├── logs/                           # Mounted log files via volume
```

---

## How It Works

1. **RabbitMQ** receives JSON messages in a queue (`incoming_texts`) with a `type` (`update`, `delete`) and data to analyze.
2. The **Python worker (async)** consumes messages using `aio-pika`.
3. Business logic (text analysis) is run in a **`ProcessPoolExecutor`** to keep the event loop non-blocking.
4. After analysis, results are stored in **MongoDB**.
5. A **final message** is published to another RabbitMQ queue (`processed_texts`).
6. If message processing fails, it is routed to (`failed_texts`) via **dead-letter exchange**.

---

## Execution

### 1. Prerequisites

Make sure you have:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- (Optional) `make`, or use manual commands

---

### 2. Launch Services

From project root:

```bash
make build
make up
```

Or manually:

```bash
docker-compose build
docker-compose up -d
```

This will start:
- RabbitMQ + management UI (http://localhost:15672)
- MongoDB
- Text analysis worker

> RabbitMQ default credentials:
> ```
> user: guest
> pass: guest
> ```

---

### 3. Expected Message Format

```json
{
  "id": "msg_158",
  "user_id": "u_2301322",
  "text": "texts",
  "timestamp": "2025-07-06T13:35:15.598473",
  "type": "update"
}
```

For `update`, the following fields are optional:
- user_id
- timestamp

For `delete`, the following fields are optional:
- user_id
- text
- timestamp

---

# Load Generator — `loadgen/`

This module simulates sending a large number of messages to **RabbitMQ** or **MongoDB** to test system performance.

---

## Structure

| File                | Role                                                               |
|---------------------|--------------------------------------------------------------------|
| `main.py`           | CLI entry point to choose target (`rabbit` or `mongo`)             |
| `rabbit_sender.py`  | Sends `update` / `delete` messages to RabbitMQ                     |
| `mongo_sender.py`   | Inserts fake documents directly into MongoDB                       |
| `config.yaml`       | Configuration file for volume and target                           |
| `requirements.txt`  | Required Python dependencies                                       |

---

## Tips

- Run `docker-compose up` before launching `loadgen`.
- Monitor in real time via:
  - RabbitMQ UI (`localhost:15672/#/queues`)
- Use `make logs` to check processing.

---

## Setup

1. Create a virtual environment:

```bash
cd loadgen
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Edit the `config.yaml` file:

```yaml
cible: rabbit         # 'rabbit' or 'mongo'
count: 20000          # total number of messages to generate
update_ratio: 0.75    # ratio between update and delete messages
```

---

## Usage

### To inject into RabbitMQ:

```bash
python main.py
```
```yaml
cible: rabbit
```

Sends `update` or `delete` messages to the `incoming_texts` queue.

---

### To populate MongoDB directly:

```bash
python main.py
```
```yaml
cible: mongo
```

Populates MongoDB with fake documents simulating messages.

---

### Logs

Worker logs are available:

- **In the terminal**:
  ```bash
  make logs
  ```

- **In mounted file** (with rotation):
  ```
  logs/worker.log
  ```

---

## Graceful Shutdown

```bash
make stop
```

Or manually:

```bash
docker-compose down
```

> The worker waits for ongoing tasks to finish before exiting.

---

# Unit Tests

The project uses `pytest` for unit testing.

---

## Run the Tests

Make sure you have activated your virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e worker
pip install -r worker/requirements-test.txt
```

Then run the tests:

```bash
make test
```

---

## Author

Mohamed Kone