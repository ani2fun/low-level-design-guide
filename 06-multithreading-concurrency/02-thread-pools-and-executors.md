---
title: "Thread Pools & Executors"
summary: "Why a thread per task fails at scale, and how Java's Executor framework replaces it: a fixed set of reused threads behind ExecutorService. execute() versus submit() and where each puts a task's exception; shutdown, awaitTermination, shutdownNow and close; what the Executors factories hide (an unbounded queue, unbounded threads); bounded queues with rejection and back-pressure; sizing a pool and the starvation deadlock a pool can cause; fixed-rate versus fixed-delay scheduling; and virtual threads. Every example runs in Java and Python, with verified output."
essential: true
---

# Thread Pools & Executors — Reusing Threads Instead of Creating Them

A ride-matching service gets a request for every rider. The obvious design starts a new thread for each request. That works in a demo but fails under load. Every thread costs memory for its stack and time to create, and ten thousand requests mean ten thousand threads competing for a handful of cores.

A **thread pool** keeps a fixed set of threads and feeds them tasks from a queue. Java's **Executor framework** packages that idea, and Python's `concurrent.futures` mirrors it. This lesson shows how to submit work to a pool, get results and failures back, shut the pool down, and set its size and limits so it stays up under load.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- An **executor** separates *what* to run (a task) from *how* it runs (which thread, when). A pool reuses a few threads for many tasks.
- `submit()` returns a `Future` that holds the task's result *or the exception it threw*. If nobody calls `get()` on that `Future`, nobody ever sees the failure.
- Every pool needs limits: a bounded queue, a rejection policy, and a size that matches the work. The `Executors` shortcuts leave the queue or the thread count unbounded.

</div>

This builds on [Multithreading & Concurrency Basics](/synapse/low-level-design/multithreading-concurrency/basics-of-multithreading-concurrency), especially `Callable`, `Future` and daemon threads. Every output below was produced by running the code on Java 21 and Python 3.11. Where timings appear, they are rounded or labeled illustrative.

**You'll be able to:** explain what a pool saves over a thread per task, and show tasks reusing a few threads; predict where a task's exception goes with `execute()` and with `submit()`; shut a pool down so that queued work either finishes or is reported; spot the unbounded queue in `newFixedThreadPool` and the unbounded threads in `newCachedThreadPool`, and replace them with a bounded `ThreadPoolExecutor`; size a pool for CPU-bound and I/O-bound work, and recognise a pool starvation deadlock; choose between fixed-rate and fixed-delay scheduling.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the executor and its queue *do*.
2. **A concrete bite** — a specific, runnable program where the mechanism produces a surprise.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [Why not a thread per task?](#1-why-not-a-thread-per-task)
2. [The Executor framework](#2-the-executor-framework)
3. [Where task exceptions go: `execute` vs `submit`](#3-where-task-exceptions-go-execute-vs-submit)
4. [Shutting a pool down](#4-shutting-a-pool-down)
5. [What the `Executors` factories hide](#5-what-the-executors-factories-hide)
6. [Bounded queues and rejection policies](#6-bounded-queues-and-rejection-policies)
7. [Sizing a pool, and pool starvation](#7-sizing-a-pool-and-pool-starvation)
8. [Scheduled pools: fixed rate vs fixed delay](#8-scheduled-pools-fixed-rate-vs-fixed-delay)
9. [Virtual threads](#9-virtual-threads)
10. [Mental-model summary](#10-mental-model-summary)
11. [Gotcha checklist](#11-gotcha-checklist)
12. [Check yourself](#-check-yourself)
13. [Sources](#-sources)

---

## 1. Why not a thread per task?

Starting a thread for every request has four costs that grow with load:

- **Memory.** Each platform thread reserves a stack, typically around 1 MB on 64-bit Linux. Ten thousand threads reserve gigabytes.
- **Creation time.** Creating and destroying an OS thread for every request is slow compared with handing the task to a thread that already exists.
- **Context switching.** With far more runnable threads than cores, the CPU spends its time switching between them instead of working ([Basics, §2](/synapse/low-level-design/multithreading-concurrency/basics-of-multithreading-concurrency)).
- **No limit.** During a traffic spike, the service keeps creating threads until the process runs out of memory. Nothing tells callers to slow down.

A pool fixes all four. A fixed number of threads is created once, and those threads take tasks from a queue. A restaurant works the same way: it employs a fixed kitchen staff and queues the orders, rather than hiring a new chef for each order. Here are nine ride requests handled by a pool of three threads:

```java run
import java.util.Set;
import java.util.concurrent.*;

public class Main {
    public static void main(String[] args) throws InterruptedException {
        ExecutorService pool = Executors.newFixedThreadPool(3);
        Set<String> workers = ConcurrentHashMap.newKeySet();

        for (int i = 1; i <= 9; i++) {
            int ride = i;
            pool.execute(() -> {
                workers.add(Thread.currentThread().getName());
                try {
                    Thread.sleep(100);  // match a rider to a driver
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
        }

        pool.shutdown();
        pool.awaitTermination(5, TimeUnit.SECONDS);
        System.out.println("9 ride requests ran on " + workers.size() + " threads:");
        workers.stream().sorted().forEach(name -> System.out.println("  " + name));
    }
}
```

```python run
import threading
import time
from concurrent.futures import ThreadPoolExecutor

workers: set[str] = set()


def match_ride(ride: int) -> None:
    workers.add(threading.current_thread().name)
    time.sleep(0.1)  # match a rider to a driver


with ThreadPoolExecutor(max_workers=3, thread_name_prefix="pool") as pool:
    for ride in range(1, 10):
        pool.submit(match_ride, ride)

print(f"9 ride requests ran on {len(workers)} threads:")
for name in sorted(workers):
    print(" ", name)
```

**Output:**
```
9 ride requests ran on 3 threads:
  pool-1-thread-1
  pool-1-thread-2
  pool-1-thread-3
```

**Analysis.** Nine tasks ran, but only three threads ever existed. Each thread took a task from the queue, ran it, and came back for the next. Python's `ThreadPoolExecutor` behaved the same way; it names its threads from the `thread_name_prefix` argument (`pool_0`, `pool_1`, `pool_2`).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** In a server, don't create a thread for each task. Submit tasks to a pool sized for the work, so the number of threads stays the same however many requests arrive.

The cost is that tasks may wait in the queue when every thread is busy. That waiting is intended: under overload, requests get slower instead of crashing the service, as long as the queue itself has a size limit (§6).

</div>

---

## 2. The Executor framework

The framework in `java.util.concurrent` is a few types:

| Type | What it is |
|---|---|
| `Executor` | one method, `execute(Runnable)`: "run this, somehow" |
| `ExecutorService` | an `Executor` you can `submit()` to for a `Future`, and shut down |
| `ThreadPoolExecutor` | the main implementation: core and maximum threads, a work queue, a rejection policy |
| `ScheduledExecutorService` | runs tasks after a delay or periodically (§8) |
| `Executors` | factory methods that build common configurations (§5) |

```d2
direction: right
caller: "Your code" { shape: rectangle }
pool: "ThreadPoolExecutor" {
  queue: "Work queue\ntask · task · task" { shape: queue }
  workers: "Worker threads\nthread-1 · thread-2 · thread-3" { shape: rectangle }
  queue -> workers: "take next task"
}
caller -> pool.queue: "execute(task) / submit(task)"
pool.workers -> caller: "Future: result or exception"
```

Two ways to hand over work:

- **`execute(Runnable)`** returns nothing. Use it when nobody needs the outcome.
- **`submit(Runnable | Callable)`** returns a `Future`. Its `get()` waits until the task ends, then returns the result or throws the task's exception ([Basics, §6](/synapse/low-level-design/multithreading-concurrency/basics-of-multithreading-concurrency)).

Python's `ThreadPoolExecutor` has only `submit()`, which always returns a `Future`. Calling `submit()` and ignoring the `Future` is the Python equivalent of `execute()`.

---

## 3. Where task exceptions go: `execute` vs `submit`

The same failing task, handed over both ways:

```java run
import java.util.concurrent.*;

public class Main {
    public static void main(String[] args) throws InterruptedException {
        ExecutorService pool = Executors.newFixedThreadPool(2);
        Runnable sendEmail = () -> {
            throw new IllegalStateException("mail server down");
        };

        System.out.println("-- execute()");
        pool.execute(sendEmail);
        Thread.sleep(200);

        System.out.println("-- submit()");
        Future<?> future = pool.submit(sendEmail);
        Thread.sleep(200);
        System.out.println("submit() printed nothing; isDone = " + future.isDone());

        try {
            future.get();
        } catch (ExecutionException e) {
            System.out.println("get() reveals it: " + e.getCause());
        }
        pool.shutdown();
    }
}
```

```python run
import time
from concurrent.futures import ThreadPoolExecutor


def send_email() -> None:
    raise RuntimeError("mail server down")


with ThreadPoolExecutor(max_workers=2) as pool:
    future = pool.submit(send_email)
    time.sleep(0.2)
    print("submit() printed nothing; done =", future.done())

    try:
        future.result()
    except RuntimeError as e:
        print("result() reveals it:", repr(e))
```

**Output (Java):**
```
-- execute()
Exception in thread "pool-1-thread-1" java.lang.IllegalStateException: mail server down
	at Main.lambda$main$0(Main.java:7)
	at java.base/java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1144)
	at java.base/java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:642)
	at java.base/java.lang.Thread.run(Thread.java:1583)
-- submit()
submit() printed nothing; isDone = true
get() reveals it: java.lang.IllegalStateException: mail server down
```

**Output (Python):**
```
submit() printed nothing; done = True
result() reveals it: RuntimeError('mail server down')
```

**Analysis.** With `execute()`, the exception escaped the task and killed the worker thread. The default handler printed its stack trace, and the pool replaced the thread. With `submit()`, nothing printed at all. The `Future` caught the exception and kept it, and it only appeared when `get()` was called. Python's `submit()` behaves the same way: the failure stays silent until someone calls `result()`.

**Intuition.**
*Mechanism.* `submit()` wraps your task in a `FutureTask`, whose `run()` catches any exception and stores it as the `Future`'s outcome <abbr title="Java SE 21 API, java.util.concurrent.FutureTask">[1]</abbr>. The worker thread sees a task that returned normally. `execute()` runs your `Runnable` directly, so an exception propagates to the thread's uncaught exception handler.

*Concrete bite.* A common bug is calling `pool.submit(this::sendInvoice)` and throwing the `Future` away. If `sendInvoice` throws, there is no log line and no stack trace. The code looks just like the `execute()` version, but it fails silently.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** If you `submit()`, keep the `Future` and call `get()` on it. If nobody will ever call `get()`, use `execute()`, or catch and log inside the task.

Checking costs a little code. Not checking means failures that leave no trace.

</div>

---

## 4. Shutting a pool down

Pool threads are not daemon threads, so a pool that is never shut down keeps the JVM running after `main` ends. There are three ways to stop a pool, and they differ in what happens to work still in the queue:

```java run
import java.util.List;
import java.util.concurrent.*;

public class Main {
    static void task(String name, long ms) {
        try {
            Thread.sleep(ms);
            System.out.println(name + " finished");
        } catch (InterruptedException e) {
            System.out.println(name + " interrupted");
        }
    }

    public static void main(String[] args) throws InterruptedException {
        ExecutorService pool = Executors.newFixedThreadPool(1);
        pool.execute(() -> task("report-1", 200));
        pool.execute(() -> task("report-2", 200));

        pool.shutdown();  // no new tasks; queued ones still run
        System.out.println("shutdown() returned at once");
        try {
            pool.execute(() -> task("report-3", 200));
        } catch (RejectedExecutionException e) {
            System.out.println("report-3 rejected after shutdown");
        }
        boolean done = pool.awaitTermination(5, TimeUnit.SECONDS);
        System.out.println("awaitTermination: all done = " + done);

        ExecutorService pool2 = Executors.newFixedThreadPool(1);
        pool2.execute(() -> task("export", 5_000));
        pool2.execute(() -> task("queued-1", 100));
        pool2.execute(() -> task("queued-2", 100));
        Thread.sleep(100);

        List<Runnable> neverStarted = pool2.shutdownNow();  // interrupt + drain the queue
        pool2.awaitTermination(5, TimeUnit.SECONDS);
        System.out.println("shutdownNow: " + neverStarted.size() + " queued tasks never started");
    }
}
```

```python run
import time
from concurrent.futures import ThreadPoolExecutor


def task(name: str, seconds: float) -> None:
    time.sleep(seconds)
    print(name, "finished")


pool = ThreadPoolExecutor(max_workers=1)
pool.submit(task, "report-1", 0.2)
pool.submit(task, "report-2", 0.2)

pool.shutdown(wait=False)  # no new tasks; queued ones still run
print("shutdown(wait=False) returned at once")
try:
    pool.submit(task, "report-3", 0.2)
except RuntimeError:
    print("report-3 rejected after shutdown")
time.sleep(0.6)

pool2 = ThreadPoolExecutor(max_workers=1)
export = pool2.submit(task, "export", 0.5)
queued = [pool2.submit(task, f"queued-{i}", 0.1) for i in (1, 2)]
time.sleep(0.1)

pool2.shutdown(wait=True, cancel_futures=True)  # drop queued tasks; running ones finish
print("cancel_futures:", sum(f.cancelled() for f in queued), "queued tasks never started")
```

**Output (Java):**
```
shutdown() returned at once
report-3 rejected after shutdown
report-1 finished
report-2 finished
awaitTermination: all done = true
export interrupted
shutdownNow: 2 queued tasks never started
```

**Output (Python):**
```
shutdown(wait=False) returned at once
report-3 rejected after shutdown
report-1 finished
report-2 finished
export finished
cancel_futures: 2 queued tasks never started
```

**Analysis.**

- `shutdown()` returned at once without waiting for anything. It only stopped new submissions, which is why `report-3` was rejected. The two reports already queued still ran.
- `awaitTermination()` is the call that waited. It returned `true` because everything finished within the 5-second limit.
- `shutdownNow()` interrupted the running `export` and returned the two tasks that had never started, so the caller can log or retry them.
- Python's `shutdown(cancel_futures=True)` also drops queued tasks, but it cannot interrupt a task that is already running, so `export` finished <abbr title="Python 3 documentation, concurrent.futures, Executor.shutdown">[8]</abbr>.

**Intuition.**
*Mechanism.* `shutdown()` starts an orderly shutdown in which "previously submitted tasks are executed, but no new tasks will be accepted"; it "does not wait" <abbr title="Java SE 21 API, java.util.concurrent.ExecutorService">[2]</abbr>. `shutdownNow()` interrupts the running tasks. That only stops a task that responds to interruption; `sleep` does, which is why `export` stopped. Since Java 19, `ExecutorService` is `AutoCloseable`: `close()` shuts down and waits, so a `try`-with-resources block does both <abbr title="Java SE 21 API, java.util.concurrent.ExecutorService.close()">[2]</abbr>. Python's `with ThreadPoolExecutor(...)` block does the same.

*Concrete bite.* A common mistake is to treat `shutdown()` as "wait for everything to finish", and then read results that are not ready yet. The calls that wait are `awaitTermination()` and `close()`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Tie each pool's lifetime to a clear scope in the code. For a short-lived pool, use `try (ExecutorService pool = …) { … }` (Python: `with`). For a long-lived one, call `shutdown()` then `awaitTermination(timeout)`, and fall back to `shutdownNow()` if the timeout passes.

The cost is deciding what should happen to a stuck task at shutdown. Tasks must check for interruption, or `shutdownNow()` cannot stop them.

</div>

---

## 5. What the `Executors` factories hide

| Factory | Threads | Queue | Fits |
|---|---|---|---|
| `newFixedThreadPool(n)` | exactly `n` | **unbounded** `LinkedBlockingQueue` | steady load with a known concurrency level |
| `newCachedThreadPool()` | **unbounded**; idle threads die after 60 s | none: each task goes straight to a thread | many short tasks, at a modest rate |
| `newSingleThreadExecutor()` | 1 | **unbounded** | tasks that must run one at a time, in order |
| `newScheduledThreadPool(n)` | `n` | a delay queue | delayed and periodic tasks (§8) |
| `newVirtualThreadPerTaskExecutor()` | a new virtual thread per task | none | many tasks that mostly wait (§9) |

These factories are convenient because they choose defaults for you, and the method names don't mention them <abbr title="Java SE 21 API, java.util.concurrent.Executors">[3]</abbr>. Here is what 1,000 slow tasks do to the first two:

```java run
import java.util.concurrent.*;

public class Main {
    static void slowTask() {
        try {
            Thread.sleep(10_000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public static void main(String[] args) throws InterruptedException {
        ThreadPoolExecutor fixed = (ThreadPoolExecutor) Executors.newFixedThreadPool(2);
        for (int i = 0; i < 1_000; i++) fixed.execute(Main::slowTask);
        System.out.println("fixed(2):  threads = " + fixed.getPoolSize()
                + ", waiting in queue = " + fixed.getQueue().size());

        ThreadPoolExecutor cached = (ThreadPoolExecutor) Executors.newCachedThreadPool();
        for (int i = 0; i < 1_000; i++) cached.execute(Main::slowTask);
        System.out.println("cached:    threads = " + cached.getPoolSize()
                + ", waiting in queue = " + cached.getQueue().size());

        fixed.shutdownNow();
        cached.shutdownNow();
    }
}
```

**Output:**
```
fixed(2):  threads = 2, waiting in queue = 998
cached:    threads = 1000, waiting in queue = 0
```

**Analysis.** The fixed pool kept its 2 threads and queued the other 998 tasks. That queue has no limit, so under sustained overload it grows until the heap runs out. The cached pool did the opposite: it created a thread for every task, 1,000 of them, and queued nothing. During a traffic spike, that is the thread-per-task design from §1 all over again. Neither pool ever refused a task.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** In a server that can be overloaded, build a `ThreadPoolExecutor` with an explicit thread count, a bounded queue and a rejection policy (§6). Use the `Executors` shortcuts for scripts, tests and work whose volume you control.

The cost is choosing two numbers (threads and queue size) and a policy up front. The benefit is a pool that fails in a predictable way instead of running out of memory.

</div>

---

## 6. Bounded queues and rejection policies

`ThreadPoolExecutor`'s constructor makes you choose every setting: the core number of threads, the maximum number, how long extra threads may sit idle, the queue, and what to do when everything is full <abbr title="Java SE 21 API, java.util.concurrent.ThreadPoolExecutor">[4]</abbr>. With two threads and a queue of two, the pool can hold at most four tasks:

```java run
import java.util.concurrent.*;

public class Main {
    static void slowTask() {
        try {
            Thread.sleep(300);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public static void main(String[] args) throws InterruptedException {
        // 2 threads, and room for 2 more tasks in the queue. Default policy: AbortPolicy.
        ThreadPoolExecutor pool = new ThreadPoolExecutor(
                2, 2, 0L, TimeUnit.MILLISECONDS, new ArrayBlockingQueue<>(2));

        for (int i = 1; i <= 6; i++) {
            try {
                pool.execute(Main::slowTask);
                System.out.println("task " + i + " accepted");
            } catch (RejectedExecutionException e) {
                System.out.println("task " + i + " rejected: pool and queue are full");
            }
        }
        pool.shutdown();
        pool.awaitTermination(5, TimeUnit.SECONDS);

        // Same pool, but overflow runs on the thread that submitted it.
        ThreadPoolExecutor backPressure = new ThreadPoolExecutor(
                2, 2, 0L, TimeUnit.MILLISECONDS, new ArrayBlockingQueue<>(2),
                new ThreadPoolExecutor.CallerRunsPolicy());
        for (int i = 1; i <= 6; i++) {
            int task = i;
            backPressure.execute(() -> {
                if (Thread.currentThread().getName().equals("main")) {
                    System.out.println("task " + task + " ran on main: the caller slowed down");
                }
                slowTask();
            });
        }
        backPressure.shutdown();
        backPressure.awaitTermination(5, TimeUnit.SECONDS);
    }
}
```

```python run
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# ThreadPoolExecutor's queue is unbounded. Bound it yourself:
# 2 workers + 2 queued = at most 4 tasks in flight.
slots = threading.BoundedSemaphore(4)


def slow_task() -> None:
    try:
        time.sleep(0.3)
    finally:
        slots.release()


with ThreadPoolExecutor(max_workers=2) as pool:
    for i in range(1, 7):
        if slots.acquire(blocking=False):
            pool.submit(slow_task)
            print(f"task {i} accepted")
        else:
            print(f"task {i} rejected: pool and queue are full")
```

**Output (Java):**
```
task 1 accepted
task 2 accepted
task 3 accepted
task 4 accepted
task 5 rejected: pool and queue are full
task 6 rejected: pool and queue are full
task 5 ran on main: the caller slowed down
```

**Output (Python):**
```
task 1 accepted
task 2 accepted
task 3 accepted
task 4 accepted
task 5 rejected: pool and queue are full
task 6 rejected: pool and queue are full
```

**Analysis.** Tasks 1 and 2 went to the two threads, tasks 3 and 4 filled the queue, and tasks 5 and 6 were rejected with `RejectedExecutionException`: the default `AbortPolicy`. The second pool used `CallerRunsPolicy`. When that pool was full, task 5 ran on `main`, the thread that submitted it. While `main` was busy running the task, it could not submit any more, so the submitting code slowed down to the pool's pace. Python's executor has no bounded queue, so the Python version limits the number of tasks in progress with a `BoundedSemaphore`, which has the same effect.

**Intuition.**
*Mechanism.* For each new task, the pool tries four things in order: run it on a free core thread; otherwise put it in the queue; otherwise start an extra thread, up to the maximum; otherwise hand it to the **rejection policy** <abbr title="Java SE 21 API, java.util.concurrent.ThreadPoolExecutor">[4]</abbr>. The built-in policies:

| Policy | When the pool is full |
|---|---|
| `AbortPolicy` (default) | throws `RejectedExecutionException` |
| `CallerRunsPolicy` | runs the task on the submitting thread: natural back-pressure |
| `DiscardPolicy` | drops the task silently |
| `DiscardOldestPolicy` | drops the oldest queued task, then retries |

*Concrete bite.* With an unbounded queue, the third step ("start an extra thread") never happens, because the queue is never full. A `ThreadPoolExecutor(2, 10, …, new LinkedBlockingQueue<>())` never grows past 2 threads. The maximum only matters with a bounded queue.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Bound the queue, and pick the rejection policy on purpose. Reject with an error (`AbortPolicy`) when the caller can retry or report "busy". Slow the caller down (`CallerRunsPolicy`) when every task must eventually run. Avoid the silent `Discard` policies unless losing work is fine.

The cost is that callers must handle a rejected task. That is better than the alternative: a process that accepts everything and then crashes.

</div>

---

## 7. Sizing a pool, and pool starvation

How many threads should a pool have? It depends on what the tasks do while they run. Brian Goetz gives this rule of thumb <abbr title="Brian Goetz et al., Java Concurrency in Practice, 2006, §8.2">[5]</abbr>:

> threads ≈ cores × target CPU utilisation × (1 + wait time ÷ compute time)

- **CPU-bound** tasks (parsing, image resizing, number crunching) hardly wait, so the wait-to-compute ratio is close to 0. That gives about **one thread per core**; Goetz suggests the number of cores plus one. More threads than that only add switching.
- **I/O-bound** tasks (calling an API, querying a database) mostly wait. A task that waits 90 ms for every 10 ms of computing has a ratio of 9, so on 4 cores about **40 threads** are needed to keep the CPUs busy.

The number must also fit whatever the tasks wait *for*. Forty threads sharing a database connection pool of 10 connections will spend most of their time waiting for a connection. Measure, then adjust.

A pool also creates a hazard that separate threads don't have. If tasks wait for *other tasks in the same pool*, they can occupy every thread while the tasks they are waiting for sit in the queue:

```java run
import java.util.concurrent.*;

public class Main {
    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newSingleThreadExecutor();

        Future<String> order = pool.submit(() -> {
            // The outer task needs a sub-result from the same pool...
            Future<String> price = pool.submit(() -> "price = 499");
            try {
                // ...and waits for it while occupying the pool's only thread.
                return price.get(1, TimeUnit.SECONDS);
            } catch (TimeoutException e) {
                return "timed out: the inner task is queued behind the task waiting for it";
            }
        });

        System.out.println(order.get());
        pool.shutdown();
    }
}
```

```python run
from concurrent.futures import ThreadPoolExecutor, TimeoutError

pool = ThreadPoolExecutor(max_workers=1)


def place_order() -> str:
    # The outer task needs a sub-result from the same pool...
    price = pool.submit(lambda: "price = 499")
    try:
        # ...and waits for it while occupying the pool's only thread.
        return price.result(timeout=1)
    except TimeoutError:
        return "timed out: the inner task is queued behind the task waiting for it"


print(pool.submit(place_order).result())
pool.shutdown()
```

**Output:**
```
timed out: the inner task is queued behind the task waiting for it
```

**Analysis.** The outer task took the pool's only thread, submitted the inner task, and waited for it. The inner task could only run on that same thread, which was busy waiting. Without the 1-second timeout, both tasks would wait forever. With a pool of `n` threads, `n` such outer tasks running at the same time cause the same hang.

**Intuition.**
*Mechanism.* This is a **thread starvation deadlock**: a task waits on work that needs a pool thread, and every pool thread is busy waiting <abbr title="Brian Goetz et al., Java Concurrency in Practice, 2006, §8.1.1">[5]</abbr>. No lock is involved, so lock-based deadlock detection does not see it.

*Concrete bite.* Tests with a large pool and light load rarely trigger it. It appears in production, when enough outer tasks arrive at the same time.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Size each pool by what its tasks do: about one thread per core for CPU-bound work, more for I/O-bound work, and never more than the resources they wait for can serve. Never block a pool thread on another task in the *same* pool. Use separate pools for dependent stages, or compose the steps without blocking (`CompletableFuture`).

Separate pools cost more configuration. One shared pool for tasks that depend on each other can cost a hang under load.

</div>

---

## 8. Scheduled pools: fixed rate vs fixed delay

A `ScheduledExecutorService` runs a task after a delay, or repeatedly. "Run it every 500 ms" can mean two different things, and the difference shows when the task itself takes time. Here the task takes 300 ms:

```java run
import java.util.concurrent.*;

public class Main {
    static long start;

    static Runnable job(String name) {
        return () -> {
            long at = (System.nanoTime() - start) / 1_000_000;
            System.out.println(name + " started at ~" + Math.round(at / 100.0) * 100 + " ms");
            try {
                Thread.sleep(300);  // the job itself takes 300 ms
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };
    }

    public static void main(String[] args) throws InterruptedException {
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
        start = System.nanoTime();
        ScheduledFuture<?> rate = scheduler.scheduleAtFixedRate(job("fixed rate "), 0, 500, TimeUnit.MILLISECONDS);
        Thread.sleep(1_300);
        rate.cancel(false);

        Thread.sleep(400);  // let the last run finish
        start = System.nanoTime();
        scheduler.scheduleWithFixedDelay(job("fixed delay"), 0, 500, TimeUnit.MILLISECONDS);
        Thread.sleep(1_900);
        scheduler.shutdownNow();
    }
}
```

```python run
import threading
import time


def job(name: str, start: float) -> None:
    at = (time.perf_counter() - start) * 1000
    print(f"{name} started at ~{round(at / 100) * 100} ms")
    time.sleep(0.3)  # the job itself takes 300 ms


def fixed_rate(period: float, runs: int) -> None:
    start = time.perf_counter()
    for k in range(runs):
        # wait until start + k * period, however long the last run took
        time.sleep(max(0.0, start + k * period - time.perf_counter()))
        job("fixed rate ", start)


def fixed_delay(delay: float, runs: int) -> None:
    start = time.perf_counter()
    for k in range(runs):
        if k:
            time.sleep(delay)  # wait `delay` after the previous run ended
        job("fixed delay", start)


fixed_rate(0.5, 3)
fixed_delay(0.5, 3)
```

**Output:**
```
fixed rate  started at ~0 ms
fixed rate  started at ~500 ms
fixed rate  started at ~1000 ms
fixed delay started at ~0 ms
fixed delay started at ~800 ms
fixed delay started at ~1600 ms
```

**Analysis.** **Fixed rate** started runs at 0, 500 and 1,000 ms: the period is measured from the *start* of one run to the *start* of the next, so the runs stay in step with the clock. **Fixed delay** started them at 0, 800 and 1,600 ms: the 500 ms delay is counted from the *end* of one run (at 300 ms) to the start of the next. Python's standard library has no periodic scheduler, so the Python version writes out both loops by hand.

**Intuition.**
*Mechanism.* With `scheduleAtFixedRate`, if a run takes longer than the period, later runs "may start late, but will not concurrently execute" <abbr title="Java SE 21 API, java.util.concurrent.ScheduledExecutorService">[6]</abbr>. With `scheduleWithFixedDelay`, the gap after each run is always the full delay. If a run throws an exception, both kinds stop silently: all later runs are cancelled.

*Concrete bite.* A session cleaner on a fixed rate that sometimes runs longer than its period will start its next run immediately, with no pause in between. On a fixed delay, it always gets the full pause.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use fixed rate for clock-like work (a metric every minute). Use fixed delay for work that needs a rest between runs (polling, cleanup). Catch exceptions inside periodic tasks, because one throw ends the schedule.

The cost of a fixed rate is a burst of back-to-back runs after a slow one. The cost of a fixed delay is drift: the runs gradually fall behind the clock.

</div>

---

## 9. Virtual threads

Java 21 adds **virtual threads**: threads managed by the JVM instead of the OS <abbr title="JEP 444: Virtual Threads">[7]</abbr>. When a virtual thread waits on I/O or `sleep`, the JVM sets it aside and frees the OS thread underneath for other work. That makes them cheap enough to create one per task, with `Executors.newVirtualThreadPerTaskExecutor()`. The Java guide's [Concurrency: High-Level & Virtual Threads](/synapse/programming-languages/java/advanced/concurrency-high-level-and-virtual-threads) runs 10,000 of them and shows when a `synchronized` block pins one to its OS thread.

For pool design, virtual threads change one thing. For work that mostly *waits*, you no longer need to size a pool to save threads; you create one virtual thread per task. Two things stay the same. CPU-bound work still needs cores, so it still belongs on a pool of about one platform thread per core. And the resources that tasks wait for still need limits. A `Semaphore` ([Locks & Semaphores](/synapse/low-level-design/multithreading-concurrency/locks-and-semaphores)) can cap the number of database connections in use, however many threads there are. Python's closest equivalent is `asyncio`, which is a different programming model.

---

## 10. Mental-model summary

| Principle | Consequence |
|---|---|
| A pool reuses a fixed set of threads for many tasks | Thread count stays fixed under load; tasks wait in a queue instead |
| `execute()` returns nothing; `submit()` returns a `Future` | `submit()` stores a task's exception in the `Future` and prints nothing |
| `shutdown()` stops new tasks and returns at once | Wait with `awaitTermination()` or `close()`; `shutdownNow()` interrupts and returns unstarted tasks |
| `newFixedThreadPool` has an unbounded queue; `newCachedThreadPool` has unbounded threads | Neither ever rejects: overload ends in memory exhaustion |
| `ThreadPoolExecutor`: core threads, then queue, then extra threads, then reject | Bound the queue; pick `AbortPolicy` or `CallerRunsPolicy` deliberately |
| Threads ≈ cores × (1 + wait ÷ compute) | ~cores for CPU-bound work; many more for I/O-bound work |
| A task waiting on a task in the same pool can starve it | Separate pools for dependent stages, or don't block |
| Fixed rate measures start to start; fixed delay end to start | A slow run causes bursts at a fixed rate; drift at a fixed delay |
| Virtual threads make blocking cheap | One per task suits waiting work; CPU-bound work still needs cores |

## 11. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

| Symptom | Likely cause | Fix |
|---|---|---|
| The program never exits after `main` ends | a pool was never shut down; its threads are non-daemon | `try`-with-resources, or `shutdown()` + `awaitTermination()` |
| A task failed and nothing was logged | it was `submit()`ted and its `Future` was ignored | call `get()`, use `execute()`, or catch and log in the task |
| Results read after `shutdown()` are missing | `shutdown()` doesn't wait | `awaitTermination()` or `close()` first |
| `shutdownNow()` didn't stop a task | the task ignores interruption | check `Thread.interrupted()`; let `InterruptedException` end the task |
| Memory grows under load, then `OutOfMemoryError` | `newFixedThreadPool`'s unbounded queue | `ThreadPoolExecutor` with a bounded queue |
| Thousands of threads appear under a spike | `newCachedThreadPool` creates a thread per waiting task | bound the maximum thread count, or use virtual threads for I/O |
| `maximumPoolSize` is never reached | the queue is unbounded, so it never fills | use a bounded queue |
| `RejectedExecutionException` | the pool and its queue are full (or the pool is shut down) | handle it: retry later, report "busy", or use `CallerRunsPolicy` |
| Tasks hang only under load | tasks block on other tasks in the same pool | separate pools, or compose without blocking |
| A periodic task silently stopped running | one run threw an exception | catch exceptions inside the task |

</div>

---

## ✅ Check yourself

One check per objective. Answer before you open anything.

```quiz
{"prompt": "A fixed pool of 3 threads is given 9 tasks. How many threads run them?", "options": ["3", "9", "12"], "answer": "3"}
```

```quiz
{"prompt": "A Runnable that throws is passed to pool.submit(), and the returned Future is ignored. What is printed?", "options": ["Nothing", "The exception's stack trace", "RejectedExecutionException"], "answer": "Nothing"}
```

```quiz
{"prompt": "pool.shutdown() is called while 5 tasks are still queued. What happens to them?", "options": ["They still run; only new submissions are rejected", "They are discarded", "They are interrupted"], "answer": "They still run; only new submissions are rejected"}
```

```quiz
{"prompt": "Executors.newFixedThreadPool(2) receives 1,000 slow tasks at once. What does it do?", "options": ["Runs 2 and queues 998, with no limit on the queue", "Rejects 998 tasks", "Starts 1,000 threads"], "answer": "Runs 2 and queues 998, with no limit on the queue"}
```

```quiz
{"prompt": "On 8 cores, which pool size fits CPU-bound image resizing best?", "options": ["About 8 or 9 threads", "About 200 threads", "1 thread"], "answer": "About 8 or 9 threads"}
```

```quiz
{"prompt": "A job takes 300 ms and is scheduled with scheduleWithFixedDelay(job, 0, 500, MILLISECONDS). When does the second run start?", "options": ["About 800 ms", "About 500 ms", "About 300 ms"], "answer": "About 800 ms"}
```

<details>
<summary>The 🧪 box below: a pool of 2 with a queue of 3 and seven tasks; the starvation example with two threads; and fixed rate with a 700 ms job.</summary>

1. Two tasks run and three wait in the queue, so tasks 1 to 5 are accepted and tasks 6 and 7 are rejected.
2. With two threads, the outer task holds one and the inner task runs on the other, so it prints `price = 499`. Two outer tasks submitted at once would hold both threads and time out again.
3. A fixed-rate schedule never runs two copies of the job at once. A 700 ms job with a 500 ms period starts at 0, 700 and 1,400 ms: every run is already late, so each one starts as soon as the previous one ends.

</details>

---

## 📚 Sources

1. `java.util.concurrent.FutureTask`, Java SE 21 API — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/FutureTask.html>
2. `java.util.concurrent.ExecutorService`, Java SE 21 API (`shutdown()`, `shutdownNow()`, `awaitTermination()`, `close()`) — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ExecutorService.html>
3. `java.util.concurrent.Executors`, Java SE 21 API — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Executors.html>
4. `java.util.concurrent.ThreadPoolExecutor`, Java SE 21 API (queuing, rejected tasks, the four policies) — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html>
5. Brian Goetz et al., *Java Concurrency in Practice* (Addison-Wesley, 2006), ch. 8, "Applying Thread Pools": §8.1.1 "Thread starvation deadlock" and §8.2 "Sizing thread pools".
6. `java.util.concurrent.ScheduledExecutorService`, Java SE 21 API — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ScheduledExecutorService.html>
7. JEP 444: Virtual Threads — <https://openjdk.org/jeps/444>
8. Python 3 documentation, `concurrent.futures` — `ThreadPoolExecutor` and `Executor.shutdown(cancel_futures=…)` — <https://docs.python.org/3/library/concurrent.futures.html>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.**

1. In §6, change the queue capacity to `3` and submit seven tasks. Predict which are accepted and which rejected.
2. In §7, change `newSingleThreadExecutor()` to `newFixedThreadPool(2)`. Predict the output.
3. In §8, make the job take 700 ms with a fixed rate of 500 ms. Predict the first three start times.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
