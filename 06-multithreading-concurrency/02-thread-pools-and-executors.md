---
title: "Thread Pools & Executors"
summary: "Why a thread per task fails at scale, and how Java's Executor framework replaces it: a fixed set of reused threads behind ExecutorService. execute() versus submit() and where each puts a task's exception; shutdown, awaitTermination, shutdownNow and close; what the Executors factories hide (an unbounded queue, unbounded threads); bounded queues with rejection and back-pressure; sizing a pool and the starvation deadlock a pool can cause; fixed-rate versus fixed-delay scheduling; and virtual threads. Every example runs in Java and Python, with verified output."
essential: true
---

# Thread Pools & Executors — Reusing Threads Instead of Creating Them

A ride-matching service gets a request for every rider. The obvious design starts a new thread per request. It works in a demo and fails under load: every thread costs memory for its stack and time to create, and ten thousand requests mean ten thousand threads competing for a handful of cores.

A **thread pool** keeps a fixed set of threads and feeds them tasks from a queue. Java's **Executor framework** packages that idea, and Python's `concurrent.futures` mirrors it. This lesson shows how to submit work, get results and failures back, shut a pool down, and size and bound it so it does not fall over.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- An **executor** separates *what* to run (a task) from *how* it runs (which thread, when). A pool reuses a few threads for many tasks.
- `submit()` returns a `Future` that holds the result *or the exception*. A failure you never `get()` is a failure nobody sees.
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
- **Creation time.** Creating and destroying an OS thread per request is slow next to handing a task to a thread that already exists.
- **Context switching.** Far more runnable threads than cores means the CPU spends its time switching, not working ([Basics, §2](/synapse/low-level-design/multithreading-concurrency/basics-of-multithreading-concurrency)).
- **No limit.** A traffic spike creates threads until the process runs out of memory. Nothing pushes back.

A pool fixes all four: a set number of threads, created once, take tasks from a queue. A restaurant hires a fixed kitchen staff and queues the orders; it does not hire a new chef per order. Nine ride requests on a pool of three:

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

**Analysis.** Nine tasks ran, but only three threads ever existed. Each thread took a task from the queue, ran it, and came back for the next. Python's `ThreadPoolExecutor` names its threads after `thread_name_prefix` (`pool_0`, `pool_1`, `pool_2`) and behaved the same.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Don't create threads per task in a server. Submit tasks to a pool sized for the work, so the thread count stays fixed however many requests arrive.

The cost is that tasks may wait in the queue when every thread is busy. That waiting is the point: it turns overload into latency instead of a crash, as long as the queue itself is bounded (§6).

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
- **`submit(Runnable | Callable)`** returns a `Future`. Its `get()` blocks until the task ends, then returns the result or throws ([Basics, §6](/synapse/low-level-design/multithreading-concurrency/basics-of-multithreading-concurrency)).

Python's `ThreadPoolExecutor` has only `submit()`, which always returns a `Future`; ignoring the `Future` is its version of `execute()`.

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

**Analysis.** With `execute()`, the exception escaped the task and killed the worker thread. The default handler printed its stack trace, and the pool replaced the thread. With `submit()`, nothing printed at all. The `Future` caught the exception and kept it; it surfaced only when `get()` was called. Python's `submit()` behaves the same way: silent until `result()`.

**Intuition.**
*Mechanism.* `submit()` wraps your task in a `FutureTask`, whose `run()` catches any exception and stores it as the `Future`'s outcome <abbr title="Java SE 21 API, java.util.concurrent.FutureTask">[1]</abbr>. The worker thread sees a task that returned normally. `execute()` runs your `Runnable` directly, so an exception propagates to the thread's uncaught exception handler.

*Concrete bite.* A common bug is `pool.submit(this::sendInvoice)` with the `Future` thrown away. If `sendInvoice` throws, there is no log line, no stack trace, nothing. The code looks like `execute()` and is quieter.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** If you `submit()`, keep the `Future` and call `get()` on it. If nobody will ever call `get()`, use `execute()`, or catch and log inside the task.

The cost of checking is a little code. The cost of not checking is failures that leave no trace.

</div>

---

## 4. Shutting a pool down

Pool threads are non-daemon, so a pool that is never shut down keeps the JVM running after `main` ends. There are three ways to stop one, and they differ in what happens to queued work:

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

- `shutdown()` returned at once. It did not wait for anything; it only stopped new submissions, which is why `report-3` was rejected. Both queued reports still ran.
- `awaitTermination()` is what waited, and it returned `true` because everything finished inside the 5-second limit.
- `shutdownNow()` interrupted the running `export` and returned the two tasks that had never started, so the caller can log or retry them.
- Python's `shutdown(cancel_futures=True)` also drops queued tasks, but it cannot interrupt a running one: `export` finished <abbr title="Python 3 documentation, concurrent.futures, Executor.shutdown">[8]</abbr>.

**Intuition.**
*Mechanism.* `shutdown()` starts an orderly shutdown in which "previously submitted tasks are executed, but no new tasks will be accepted"; it "does not wait" <abbr title="Java SE 21 API, java.util.concurrent.ExecutorService">[2]</abbr>. `shutdownNow()` interrupts running tasks, which only stops a task that responds to interruption, as `sleep` does. Since Java 19, `ExecutorService` is `AutoCloseable`: `close()` shuts down and waits, so a `try`-with-resources block does both <abbr title="Java SE 21 API, java.util.concurrent.ExecutorService.close()">[2]</abbr>. Python's `with ThreadPoolExecutor(...)` block does the same.

*Concrete bite.* Treating `shutdown()` as "wait for everything", then reading results that are not ready yet. The wait is `awaitTermination()` or `close()`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Tie a pool's life to a scope. For a short-lived pool, use `try (ExecutorService pool = …) { … }` (Python: `with`). For a long-lived one, call `shutdown()` then `awaitTermination(timeout)`, and fall back to `shutdownNow()` if the timeout passes.

The cost is deciding what a stuck task should do on shutdown. Tasks must check for interruption, or `shutdownNow()` cannot stop them.

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

The convenience comes from defaults the names don't show <abbr title="Java SE 21 API, java.util.concurrent.Executors">[3]</abbr>. Here is what 1,000 slow tasks do to the first two:

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

**Analysis.** The fixed pool kept its 2 threads and queued the other 998 tasks. That queue has no limit, so under sustained overload it grows until the heap runs out. The cached pool did the opposite: it created a thread for every task, 1,000 of them, with nothing queued. Under a spike that is the thread-per-task design from §1 again. Neither pool ever said no.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** In a server that can be overloaded, build a `ThreadPoolExecutor` with an explicit thread count, a bounded queue and a rejection policy (§6). Use the `Executors` shortcuts for scripts, tests and work whose volume you control.

The cost is choosing two numbers and a policy up front. The benefit is a pool that fails predictably instead of running out of memory.

</div>

---

## 6. Bounded queues and rejection policies

`ThreadPoolExecutor`'s constructor exposes every decision: core threads, maximum threads, how long extra threads idle, the queue, and what to do when everything is full <abbr title="Java SE 21 API, java.util.concurrent.ThreadPoolExecutor">[4]</abbr>. Two threads and a queue of two hold at most four tasks:

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

**Analysis.** Tasks 1 and 2 went to the two threads, tasks 3 and 4 filled the queue, and tasks 5 and 6 were rejected with `RejectedExecutionException`: the default `AbortPolicy`. The second pool used `CallerRunsPolicy`. When it was full, task 5 ran on `main`, the thread that submitted it. While `main` was busy running it, it could not submit more, so the producer slowed to the pool's pace. Python's executor has no bounded queue, so the Python version caps tasks in flight with a `BoundedSemaphore`, the same idea.

**Intuition.**
*Mechanism.* The pool runs a new task on a core thread if one is free, else queues it, else starts an extra thread up to the maximum, else hands it to the **rejection policy** <abbr title="Java SE 21 API, java.util.concurrent.ThreadPoolExecutor">[4]</abbr>. The built-in policies:

| Policy | When the pool is full |
|---|---|
| `AbortPolicy` (default) | throws `RejectedExecutionException` |
| `CallerRunsPolicy` | runs the task on the submitting thread: natural back-pressure |
| `DiscardPolicy` | drops the task silently |
| `DiscardOldestPolicy` | drops the oldest queued task, then retries |

*Concrete bite.* With an unbounded queue, "start an extra thread up to the maximum" never happens, because the queue is never full. A `ThreadPoolExecutor(2, 10, …, new LinkedBlockingQueue<>())` never grows past 2 threads. The maximum only matters with a bounded queue.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Bound the queue, and pick the rejection policy on purpose. Reject with an error (`AbortPolicy`) when the caller can retry or report "busy". Slow the caller down (`CallerRunsPolicy`) when every task must eventually run. Avoid the silent `Discard` policies unless losing work is fine.

The cost is that callers must handle rejection. That is better than the alternative: a process that accepts everything and then dies.

</div>

---

## 7. Sizing a pool, and pool starvation

How many threads? It depends on what the tasks do while they run. Brian Goetz's sizing rule <abbr title="Brian Goetz et al., Java Concurrency in Practice, 2006, §8.2">[5]</abbr>:

> threads ≈ cores × target CPU utilisation × (1 + wait time ÷ compute time)

- **CPU-bound** tasks (parsing, image resizing, number crunching) barely wait, so the ratio is near 0: about **one thread per core**. Goetz suggests cores + 1. More threads only add switching.
- **I/O-bound** tasks (calling an API, querying a database) mostly wait. A task that waits 90 ms for each 10 ms of computing has a ratio of 9: on 4 cores, about **40 threads** keep the CPUs busy.

The count must also respect what the tasks wait *on*: 40 threads sharing a database connection pool of 10 will mostly wait for connections. Measure, then adjust.

A pool also creates a hazard that raw threads don't have. Tasks that wait for *other tasks in the same pool* can occupy every thread while the tasks they wait for sit in the queue:

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

**Analysis.** The outer task took the pool's only thread, submitted the inner task, and waited for it. The inner task could only run on that same thread, which was busy waiting. Without the 1-second timeout, both would wait forever. With a pool of `n` threads, `n` such outer tasks at once produce the same hang.

**Intuition.**
*Mechanism.* This is a **thread starvation deadlock**: a task waits on work that needs a pool thread, and every pool thread is busy waiting <abbr title="Brian Goetz et al., Java Concurrency in Practice, 2006, §8.1.1">[5]</abbr>. No lock is involved, so lock-based deadlock detection does not see it.

*Concrete bite.* It hides in tests with a large pool and light load, then appears in production when enough outer tasks arrive together.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Size pools by what tasks do: about one thread per core for CPU-bound work, more for I/O-bound work, capped by the resources they wait on. Never block a pool thread on another task in the *same* pool. Use separate pools for dependent stages, or compose the steps without blocking (`CompletableFuture`).

The cost of separate pools is more configuration. The cost of one shared pool for dependent tasks is a hang under load.

</div>

---

## 8. Scheduled pools: fixed rate vs fixed delay

A `ScheduledExecutorService` runs a task after a delay, or repeatedly. There are two kinds of "every 500 ms", and they differ when the task takes time. Here the task takes 300 ms:

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

**Analysis.** **Fixed rate** started runs at 0, 500 and 1,000 ms: the period is measured from *start to start*, so the schedule keeps to the clock. **Fixed delay** started them at 0, 800 and 1,600 ms: the 500 ms delay is counted from the *end* of one run (at 300 ms) to the start of the next. Python's standard library has no periodic scheduler, so the Python version spells out both loops.

**Intuition.**
*Mechanism.* With `scheduleAtFixedRate`, if a run takes longer than the period, later runs "may start late, but will not concurrently execute" <abbr title="Java SE 21 API, java.util.concurrent.ScheduledExecutorService">[6]</abbr>. With `scheduleWithFixedDelay`, the gap after each run is always the full delay. If a run throws, both stop the schedule silently: later runs are cancelled.

*Concrete bite.* A session cleaner on a fixed rate that sometimes takes longer than its period runs back-to-back with no rest. On a fixed delay it always gets its gap.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use fixed rate for clock-like work (a metric every minute). Use fixed delay for work that needs a rest between runs (polling, cleanup). Catch exceptions inside periodic tasks, because one throw ends the schedule.

The cost of fixed rate is bursts after a slow run. The cost of fixed delay is drift: runs slide later than the clock.

</div>

---

## 9. Virtual threads

Java 21 adds **virtual threads**: threads managed by the JVM instead of the OS <abbr title="JEP 444: Virtual Threads">[7]</abbr>. When one blocks on I/O or `sleep`, the JVM parks it and frees the OS thread underneath, so they are cheap enough to create one per task with `Executors.newVirtualThreadPerTaskExecutor()`. The Java guide's [Concurrency: High-Level & Virtual Threads](/synapse/programming-languages/java/advanced/concurrency-high-level-and-virtual-threads) runs 10,000 of them and shows when a `synchronized` block pins one to its OS thread.

For pool design, they change one thing. For *waiting* work, you no longer size a pool to save threads; you create a virtual thread per task. Two things stay the same. CPU-bound work still needs cores, so it still belongs on a pool of about one platform thread per core. And the resources tasks wait on still need limits: a `Semaphore` ([Locks & Semaphores](/synapse/low-level-design/multithreading-concurrency/locks-and-semaphores)) caps database connections however many threads there are. Python's closest analogue is `asyncio`, a different programming model.

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

1. Two tasks run, three wait in the queue, and the other two are rejected: `5 accepted`, then two `rejected` lines.
2. With two threads, the outer task holds one and the inner task runs on the other, so it prints `price = 499`. Two outer tasks submitted at once would hold both threads and time out again.
3. Fixed rate never runs two copies at once. A 700 ms job with a 500 ms period starts at 0, 700 and 1,400 ms: each run starts as soon as the previous one ends, because each is already late.

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
