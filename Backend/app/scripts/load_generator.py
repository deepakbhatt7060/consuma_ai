import asyncio
import random
import httpx
import sys
import time
import uuid
import statistics

BASE_URL = "http://localhost:8000"

TOTAL_REQUESTS = 500
CONCURRENCY = 10
TIMEOUT = 10

# -------------------------
# Globals (metrics)
# -------------------------

success = 0
failure = 0

sync_latencies = []

CALLBACK_BASE_URL = None


# -------------------------
# Helpers
# -------------------------

def percentile(data, p):
    if not data:
        return 0
    return statistics.quantiles(data, n=100)[p - 1]


# -------------------------
# Request functions
# -------------------------

async def fire_sync(client):
    global success, failure

    start = time.perf_counter()
    try:
        resp = await client.post(
            "/sync",
            json={"number": random.randint(1, 40)}
        )
        latency = time.perf_counter() - start
        sync_latencies.append(latency)

        if resp.status_code == 200:
            success += 1
        else:
            failure += 1

    except Exception:
        failure += 1


async def fire_async(client):
    global success, failure

    try:
        resp = await client.post(
            "/async",
            json={
                "number": random.randint(1, 40),
                "callback_url": CALLBACK_BASE_URL,
            }
        )

        if resp.status_code == 200:
            success += 1
        else:
            failure += 1

    except Exception:
        failure += 1


# -------------------------
# Load runner
# -------------------------

async def run_load(request_fn):
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=TIMEOUT
    ) as client:
        semaphore = asyncio.Semaphore(CONCURRENCY)

        async def guarded():
            async with semaphore:
                await request_fn(client)

        await asyncio.gather(
            *[guarded() for _ in range(TOTAL_REQUESTS)]
        )


# -------------------------
# Report writers
# -------------------------

def write_sync_report():
    with open("sync_report.txt", "w") as f:
        f.write("SYNC LOAD TEST REPORT\n")
        f.write("=====================\n\n")
        f.write(f"Total Requests: {TOTAL_REQUESTS}\n")
        f.write(f"Success: {success}\n")
        f.write(f"Failure: {failure}\n\n")

        f.write("Latency (seconds):\n")
        f.write(f"p50: {percentile(sync_latencies, 50):.4f}\n")
        f.write(f"p95: {percentile(sync_latencies, 95):.4f}\n")
        f.write(f"p99: {percentile(sync_latencies, 99):.4f}\n")


def write_async_report():
    with open("async_report.txt", "w") as f:
        f.write("ASYNC LOAD TEST REPORT\n")
        f.write("=====================\n\n")
        f.write(f"Total Requests Sent: {TOTAL_REQUESTS}\n")
        f.write(f"Accepted (2xx/3xx): {success}\n")
        f.write(f"Failed: {failure}\n\n")

        f.write(
            "NOTE:\n"
            "Time-to-callback is not measurable client-side when using a generic callback URL.\n"
            "It can be viewed from UI for each request from Request Details by Mode providing async as input.\n"
        )


# -------------------------
# Main
# -------------------------

async def main():
    global CALLBACK_BASE_URL

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python load_generator.py sync")
        print("  python load_generator.py async <callback_url>")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "sync":
        print("Starting SYNC request storm...")
        await run_load(fire_sync)
        write_sync_report()

    elif mode == "async":
        if len(sys.argv) != 3:
            print("Usage: python load_generator.py async <callback_url>")
            sys.exit(1)

        CALLBACK_BASE_URL = sys.argv[2]

        print("Starting ASYNC request storm...")
        await run_load(fire_async)

        write_async_report()

    else:
        print("Invalid mode. Use 'sync' or 'async'.")
        sys.exit(1)

    print("Load generation completed.")


if __name__ == "__main__":
    asyncio.run(main())
