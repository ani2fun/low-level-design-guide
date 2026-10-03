---
title: "Producer-Consumer"
summary: "The pattern behind job queues, log shippers and online judges: producers put work into a bounded buffer and consumers take it out, so each side runs at its own pace. A bounded buffer built on a monitor, and why its waits sit in while loops; BlockingQueue, which does it for you; back-pressure when producers outrun consumers, and rejecting with a timeout instead of hanging; stopping consumers cleanly with poison pills; and choosing a queue type and capacity. Every example runs in Java and Python, with verified output."
essential: true
---

# Producer-Consumer — Decoupling Work With a Bounded Queue

An online judge receives code submissions in bursts: when a contest starts, hundreds arrive within a minute. Each one takes seconds to compile and run. The web server that receives the submissions should not have to wait for the judge, and the judge should not receive work faster than it can handle it.

The **producer-consumer** pattern puts a **buffer** between the two sides. **Producers** add work to it, **consumers** take work from it, and each side runs at its own pace. This lesson first builds a buffer with a size limit by hand, to show how it works, and then uses `BlockingQueue`, the ready-made version you should use in real code.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- A buffer separates producers from consumers: it absorbs bursts of work, and each side can be scaled up independently.
- The buffer must be **bounded**, meaning it has a maximum size. When it is full, a producer must wait, be turned away, or throw work away. Slowing producers down this way is called **back-pressure**, and which option to use is a design decision.
- Use a `BlockingQueue` (in Python, `queue.Queue`) rather than writing `wait`/`notify` code by hand, and stop the consumers by sending each one a **poison pill**: a special item that means "no more work".

</div>

This builds on [Locks & Semaphores](/synapse/low-level-design/multithreading-concurrency/locks-and-semaphores). How `wait` and `notify` work in Java, including what goes wrong when you use `if` instead of `while`, is covered in the Java guide's [Concurrency: Coordination](/synapse/programming-languages/java/advanced/concurrency-coordination). Every output below was produced by running the code on Java 21 and Python 3.11.

**You'll be able to:** explain what a buffer between producers and consumers gives you; build a bounded buffer on a monitor and say why each wait is in a `while` loop; replace it with a `BlockingQueue`; choose between blocking, rejecting and dropping when the queue is full; shut down a pool of consumers with poison pills; pick a queue type and a capacity.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the queue and its waiting threads *do*.
2. **A concrete bite** — a specific, runnable program where the mechanism produces a surprise.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [Why put a buffer between them?](#1-why-put-a-buffer-between-them)
2. [A bounded buffer on a monitor](#2-a-bounded-buffer-on-a-monitor)
3. [`BlockingQueue`: the buffer done for you](#3-blockingqueue-the-buffer-done-for-you)
4. [When the queue is full: back-pressure](#4-when-the-queue-is-full-back-pressure)
5. [Choosing a queue](#5-choosing-a-queue)
6. [Mental-model summary](#6-mental-model-summary)
7. [Gotcha checklist](#7-gotcha-checklist)
8. [Check yourself](#-check-yourself)
9. [Sources](#-sources)

---

## 1. Why put a buffer between them?

Without a buffer, a producer hands work directly to a consumer and waits for it to finish. The web server would keep every user's request open while the judge compiles their code. A buffer changes three things:

- **Independence.** The producer can carry on as soon as the work is in the queue. Producers and consumers don't know about each other, only about the queue.
- **Absorbing bursts.** The first minute of a contest fills the queue, and the judges work through it over the next few minutes.
- **Separate scaling.** Add consumers when the queue keeps growing; add producers when it stays empty.

```d2
direction: right
producers: "Producers\nweb servers" { shape: rectangle }
queue: "Bounded queue\ncapacity N" { shape: queue }
consumers: "Consumers\njudge workers" { shape: rectangle }
producers -> queue: "put: waits when full"
queue -> consumers: "take: waits when empty"
```

A coffee machine and a customer are the smallest example: a buffer that holds one cup. The machine must not pour into a cup that is already full, and the customer must wait while the cup is empty. Every buffer follows the same two rules: **don't add when it is full, and don't take when it is empty**.

---

## 2. A bounded buffer on a monitor

Building a buffer by hand shows what every blocking queue does inside. Here, a fast producer places orders into a buffer that holds two, and a slower kitchen takes them out:

```java run
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;

// A bounded buffer built on the object's monitor.
class BoundedBuffer<T> {
    private final Queue<T> items = new ArrayDeque<>();
    private final int capacity;
    private int peak = 0;

    BoundedBuffer(int capacity) {
        this.capacity = capacity;
    }

    synchronized void put(T item) throws InterruptedException {
        while (items.size() == capacity) wait();  // full: wait for a take
        items.add(item);
        peak = Math.max(peak, items.size());
        notifyAll();                              // wake any waiting taker
    }

    synchronized T take() throws InterruptedException {
        while (items.isEmpty()) wait();           // empty: wait for a put
        T item = items.remove();
        notifyAll();                              // wake any waiting putter
        return item;
    }

    synchronized int peak() {
        return peak;
    }
}

public class Main {
    public static void main(String[] args) throws InterruptedException {
        BoundedBuffer<Integer> orders = new BoundedBuffer<>(2);
        List<Integer> handled = new ArrayList<>();

        Thread kitchen = new Thread(() -> {
            try {
                for (int i = 0; i < 6; i++) {
                    handled.add(orders.take());
                    Thread.sleep(50);  // the consumer is slower than the producer
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        kitchen.start();

        for (int order = 1; order <= 6; order++) orders.put(order);  // the fast producer
        kitchen.join();
        System.out.println("orders handled, in order: " + handled);
        System.out.println("most orders ever waiting: " + orders.peak());
    }
}
```

```python run
import threading
import time
from collections import deque


# A bounded buffer built on a Condition (a lock plus wait/notify).
class BoundedBuffer:
    def __init__(self, capacity: int) -> None:
        self._items: deque = deque()
        self._capacity = capacity
        self._changed = threading.Condition()
        self.peak = 0

    def put(self, item) -> None:
        with self._changed:
            while len(self._items) == self._capacity:  # full: wait for a take
                self._changed.wait()
            self._items.append(item)
            self.peak = max(self.peak, len(self._items))
            self._changed.notify_all()                 # wake any waiting taker

    def take(self):
        with self._changed:
            while not self._items:                     # empty: wait for a put
                self._changed.wait()
            item = self._items.popleft()
            self._changed.notify_all()                 # wake any waiting putter
            return item


orders = BoundedBuffer(2)
handled: list[int] = []


def kitchen() -> None:
    for _ in range(6):
        handled.append(orders.take())
        time.sleep(0.05)  # the consumer is slower than the producer


consumer = threading.Thread(target=kitchen)
consumer.start()
for order in range(1, 7):
    orders.put(order)  # the fast producer
consumer.join()
print("orders handled, in order:", handled)
print("most orders ever waiting:", orders.peak)
```

**Output:**
```
orders handled, in order: [1, 2, 3, 4, 5, 6]
most orders ever waiting: 2
```

**Analysis.** All six orders were handled, in the order they were placed, and the buffer never held more than two. The producer was faster, so it often found the buffer full and waited inside `put()`. Each `take()` made room and woke the producer up. Python's `threading.Condition` is a lock with `wait` and `notify` methods, the same pair a Java monitor provides <abbr title="Python 3 documentation, threading, Condition objects">[4]</abbr>.

**Intuition.**
*Mechanism.* `wait()` releases the monitor and sleeps until another thread calls `notify` or `notifyAll` on the same object. Before returning, it takes the monitor back <abbr title="Java SE 21 API, java.lang.Object.wait()">[1]</abbr>. Both `put` and `take` hold the monitor while they check and change `items`, so checking and changing happen as one atomic step.

*Concrete bite.* Each `wait()` sits inside a `while` loop, not an `if`. A thread can wake up while the condition is still false: another consumer may have taken the item first, `notifyAll` wakes up every waiting thread, and the JVM even allows **spurious wake-ups**, where a thread wakes with no notify at all <abbr title="Java SE 21 API, java.lang.Object.wait()">[1]</abbr>. The loop checks the condition again after every wake-up. With `if`, a consumer that woke up too early would call `remove()` on an empty queue. The Java guide's [Concurrency: Coordination, §1](/synapse/programming-languages/java/advanced/concurrency-coordination) runs that failure.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** If you write a wait yourself, write it as `while (!condition) wait();` inside the lock, and use `notifyAll()` when producers and consumers wait on the same monitor.

The cost of writing this coordination by hand is that every one of these details must be right. That is why the next section replaces it with a library class.

</div>

---

## 3. `BlockingQueue`: the buffer done for you

`java.util.concurrent.BlockingQueue` is a thread-safe queue whose `put()` waits while it is full and whose `take()` waits while it is empty <abbr title="Java SE 21 API, java.util.concurrent.BlockingQueue">[2]</abbr>. Python's `queue.Queue(maxsize=…)` works the same way <abbr title="Python 3 documentation, queue — A synchronized queue class">[3]</abbr>. Here is the online judge with one fast producer, two slow judges, and room for three submissions to wait in the queue:

```java run
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class Main {
    record Submission(int id, String user) {}
    static final Submission POISON = new Submission(-1, "");  // "no more work"

    public static void main(String[] args) throws InterruptedException {
        BlockingQueue<Submission> queue = new ArrayBlockingQueue<>(3);
        AtomicInteger judged = new AtomicInteger();
        int judges = 2;

        Runnable judge = () -> {
            try {
                while (true) {
                    Submission s = queue.take();       // waits while the queue is empty
                    if (s == POISON) return;
                    Thread.sleep(100);                 // compile, run, compare: slow
                    judged.incrementAndGet();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };
        Thread[] workers = new Thread[judges];
        for (int i = 0; i < judges; i++) {
            workers[i] = new Thread(judge, "judge-" + (i + 1));
            workers[i].start();
        }

        String[] users = {"alice", "bob", "carol"};
        long start = System.nanoTime();
        for (int id = 1; id <= 8; id++) {
            queue.put(new Submission(id, users[id % 3]));  // waits while the queue is full
        }
        long producerMs = (System.nanoTime() - start) / 1_000_000;
        for (int i = 0; i < judges; i++) queue.put(POISON);  // one pill per consumer
        for (Thread w : workers) w.join();

        System.out.println("judged " + judged.get() + " of 8 submissions");
        System.out.println("producer spent ~" + Math.round(producerMs / 100.0) * 100
                + " ms blocked on a full queue, instead of ~0 ms");
    }
}
```

```python run
import queue
import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Submission:
    id: int
    user: str


POISON = Submission(-1, "")  # "no more work"
submissions: "queue.Queue[Submission]" = queue.Queue(maxsize=3)
judged = 0
judged_lock = threading.Lock()
judges = 2


def judge() -> None:
    global judged
    while True:
        s = submissions.get()  # waits while the queue is empty
        if s is POISON:
            return
        time.sleep(0.1)        # compile, run, compare: slow
        with judged_lock:
            judged += 1


workers = [threading.Thread(target=judge, name=f"judge-{i}") for i in range(1, judges + 1)]
for w in workers:
    w.start()

users = ["alice", "bob", "carol"]
start = time.perf_counter()
for i in range(1, 9):
    submissions.put(Submission(i, users[i % 3]))  # waits while the queue is full
producer_ms = (time.perf_counter() - start) * 1000
for _ in range(judges):
    submissions.put(POISON)  # one pill per consumer
for w in workers:
    w.join()

print(f"judged {judged} of 8 submissions")
print(f"producer spent ~{round(producer_ms / 100) * 100} ms blocked on a full queue, instead of ~0 ms")
```

**Output** *(illustrative — the blocked time is rounded and can vary slightly):*
```
judged 8 of 8 submissions
producer spent ~200 ms blocked on a full queue, instead of ~0 ms
```

**Analysis.** All eight submissions were judged. The producer could not get far ahead of the judges: once three submissions were waiting, `put()` made it wait until a judge took one. That waiting is **back-pressure**: the slow side automatically slows the fast side down, and memory use stays limited.

To shut down, the producer added one `POISON` submission for each judge, and each judge stops when it takes one. A poison pill is just a value that the consumers recognise as "no more work". It goes into the queue behind all the real work, so nothing already queued is lost.

**Intuition.**
*Mechanism.* The queue contains the lock, the two conditions ("not full" and "not empty") and the `while` loops from §2. So the producer and consumer code needs no locking of its own.

*Concrete bite: one pill per consumer.* With two judges and only one pill, the first judge to take it stops, and the second waits in `take()` forever, so the program never ends. Send exactly as many pills as there are consumers, or use an executor's `shutdown()` ([Thread Pools & Executors](/synapse/low-level-design/multithreading-concurrency/thread-pools-and-executors)), which uses the same pattern with a queue built in.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** For producer-consumer inside one process, use a `BlockingQueue` with a size limit (in Python, `queue.Queue(maxsize=…)`). Stop the consumers with one poison pill each, or let an executor manage the queue.

The cost is choosing a capacity (§5). The benefit is coordination code you don't have to write, test or debug yourself.

</div>

---

## 4. When the queue is full: back-pressure

If producers stay faster than consumers for long enough, the queue fills up. Then something has to give, and what gives should be decided in the design:

| Policy | Java | Python | Effect |
|---|---|---|---|
| **Block** the producer | `put(e)` | `put(item)` | the producer slows down to the consumers' pace |
| **Wait a while, then reject** | `offer(e, timeout, unit)` returns `false` | `put(item, timeout=…)` raises `queue.Full` | the caller can tell the user "busy, please retry" |
| **Reject at once** | `offer(e)` returns `false` | `put_nowait(item)` raises `queue.Full` | fails immediately |
| **Drop** | `offer` and ignore the result, or remove the oldest item first | — | keeps only recent data, such as metrics samples |

Making a web request wait for minutes is rarely acceptable, so the judge's web front end should reject submissions instead. Here, every judge is busy and the queue has two places left:

```java run
import java.util.concurrent.*;

public class Main {
    public static void main(String[] args) throws InterruptedException {
        BlockingQueue<String> queue = new ArrayBlockingQueue<>(2);  // the judges are all busy

        for (String user : new String[] {"alice", "bob", "carol", "dave"}) {
            // Wait at most 100 ms for space, then tell the user instead of hanging.
            boolean accepted = queue.offer(user + "'s submission", 100, TimeUnit.MILLISECONDS);
            System.out.println(user + (accepted ? ": queued" : ": server busy, please retry"));
        }
        System.out.println("queued: " + queue);
    }
}
```

```python run
import queue

submissions: "queue.Queue[str]" = queue.Queue(maxsize=2)  # the judges are all busy

for user in ["alice", "bob", "carol", "dave"]:
    try:
        # Wait at most 100 ms for space, then tell the user instead of hanging.
        submissions.put(f"{user}'s submission", timeout=0.1)
        print(f"{user}: queued")
    except queue.Full:
        print(f"{user}: server busy, please retry")
print("queued:", list(submissions.queue))
```

**Output:**
```
alice: queued
bob: queued
carol: server busy, please retry
dave: server busy, please retry
queued: [alice's submission, bob's submission]
```

**Analysis.** Alice and Bob filled the two places. Carol and Dave each waited 100 ms for space, found none, and were told to retry. Their requests did not hold up a web server thread until a judge became free.

**Intuition.**
*Mechanism.* A bounded queue turns overload into a visible signal: a full queue. An unbounded queue hides the overload. A `LinkedBlockingQueue` created without a capacity accepts everything, and under constant overload it grows until the process runs out of memory. That is the same failure as `newFixedThreadPool`'s queue in [Thread Pools & Executors, §5](/synapse/low-level-design/multithreading-concurrency/thread-pools-and-executors).

*Concrete bite.* "Let's just make the queue very big" only moves the problem. If a queue holds a million submissions and the judges need an hour to work through them, every new user waits an hour. Rejecting early is kinder to the user.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** For each producer, decide what happens when the queue is full: block for background producers, wait briefly and then reject for user-facing ones, and drop only data that is allowed to be lost. Never leave a queue without a size limit by accident.

Rejecting costs a "busy" path in the client, and retries that wait before trying again. Not deciding costs an outage.

</div>

---

## 5. Choosing a queue

| Queue | Bounded? | Order | Fits |
|---|---|---|---|
| `ArrayBlockingQueue` | yes, fixed at creation | FIFO | the default bounded buffer |
| `LinkedBlockingQueue` | optional (no limit by default) | FIFO | always pass a capacity; uses separate locks for put and take |
| `PriorityBlockingQueue` | no | by priority | for example, paid users' submissions first; add a limit yourself |
| `SynchronousQueue` | stores nothing at all | direct hand-off | each `put` waits for a matching `take` |
| `DelayQueue` | no | by when each item's delay ends | retries and timeouts that become ready later |

Python's `queue` module offers `Queue` (FIFO), `LifoQueue` and `PriorityQueue`, and each one takes a `maxsize` limit.

**How big should the queue be?** Size it by how long users can be made to wait, not by how much memory you have. If two judges together finish about 20 submissions a minute, and users will accept a 3-minute wait, a capacity of around 60 is right. Beyond that, reject submissions and let users retry, or add more judges.

Between separate *processes* or *machines*, the same pattern uses a message broker (Kafka, RabbitMQ, SQS) instead of a queue in memory. The broker keeps messages safe if a process crashes, and lets producers and consumers run on different machines. The choices about what to do when the queue is full stay the same.

---

## 6. Mental-model summary

| Principle | Consequence |
|---|---|
| A buffer separates producers from consumers | Bursts are absorbed; each side scales independently |
| Don't add when full, don't take when empty | `put` waits on "not full", `take` waits on "not empty" |
| Waits go inside `while` loops | A thread can wake up while the condition is still false; always check again |
| `BlockingQueue` / `queue.Queue` contain the lock, the conditions and the loops | Producer and consumer code needs no locking of its own |
| A bounded queue creates back-pressure | Memory use stays limited; the fast side slows down or is told "busy" |
| When the queue is full: block, wait and then reject, or drop | Choose for each producer; user-facing code should not wait long |
| One poison pill per consumer | Fewer pills leave consumers waiting forever |
| Size the queue by acceptable waiting time | A huge queue only hides overload |

## 7. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

| Symptom | Likely cause | Fix |
|---|---|---|
| `NoSuchElementException` from a hand-written buffer | `if` instead of `while` around `wait()` | `while (empty) wait();` |
| Hand-written buffer hangs with items waiting | `notify()` woke a thread of the wrong kind | `notifyAll()`, or a `BlockingQueue` |
| `IllegalMonitorStateException` from `wait()` | called without holding that object's monitor | call it inside `synchronized` on the same object |
| Memory grows steadily under load | an unbounded queue (`LinkedBlockingQueue()` with no capacity) | give it a capacity and a full-queue policy |
| Request threads hang when the system is busy | user-facing producers use blocking `put()` | `offer(timeout)` / `put(timeout=…)`, then reject |
| The program never exits after the work is done | fewer poison pills than consumers | one pill per consumer, or an executor's `shutdown()` |
| Work disappears silently | `offer()` returned `false` and nobody checked | handle the `false` (or `queue.Full`) |

</div>

---

## ✅ Check yourself

One check per objective. Answer before you open anything.

```quiz
{"prompt": "What does a bounded queue between a web server and slow workers give the web server?", "options": ["It can return as soon as work is queued, and is slowed or told busy when the queue is full", "Faster workers", "Guaranteed processing order across all servers"], "answer": "It can return as soon as work is queued, and is slowed or told busy when the queue is full"}
```

```quiz
{"prompt": "In a hand-written buffer, why is it while (items.isEmpty()) wait(); and not if?", "options": ["A thread can wake while the buffer is still empty, so it must re-check", "while is faster than if", "if does not compile inside synchronized"], "answer": "A thread can wake while the buffer is still empty, so it must re-check"}
```

```quiz
{"prompt": "A producer calls put() on a full ArrayBlockingQueue. What happens?", "options": ["It waits until a consumer takes an element", "It throws IllegalStateException", "The oldest element is dropped"], "answer": "It waits until a consumer takes an element"}
```

```quiz
{"prompt": "A user-facing endpoint enqueues work. Which call fits best when the queue may be full?", "options": ["offer(item, 100, MILLISECONDS), and reply 'busy' if it returns false", "put(item)", "add(item) inside an empty catch block"], "answer": "offer(item, 100, MILLISECONDS), and reply 'busy' if it returns false"}
```

```quiz
{"prompt": "Three consumer threads loop on take() and exit on a poison pill. The producer sends one pill. What happens?", "options": ["One consumer exits; two wait forever", "All three exit", "The queue throws an exception"], "answer": "One consumer exits; two wait forever"}
```

```quiz
{"prompt": "Which queue never holds elements, so each put waits for a matching take?", "options": ["SynchronousQueue", "ArrayBlockingQueue", "PriorityBlockingQueue"], "answer": "SynchronousQueue"}
```

<details>
<summary>The 🧪 box below: four judges instead of two; a queue of capacity 1; and one poison pill for two judges.</summary>

1. Four judges empty the queue twice as fast, so the producer finds it full less often: in our run its blocked time fell from about 200 ms to about 100 ms. All 8 are still judged.
2. With capacity 1, at most one submission waits, so the producer blocks more: about 300 ms in our run. The result is the same 8 of 8.
3. With one pill and two judges, one judge exits and the other waits in `take()` forever, so `join()` never returns and the program hangs.

</details>

---

## 📚 Sources

1. `java.lang.Object`, Java SE 21 API (`wait()`, `notify()`, `notifyAll()`, spurious wake-ups) — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html>
2. `java.util.concurrent.BlockingQueue`, Java SE 21 API — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/BlockingQueue.html>
3. Python 3 documentation, `queue` — A synchronized queue class — <https://docs.python.org/3/library/queue.html>
4. Python 3 documentation, `threading` — Condition objects — <https://docs.python.org/3/library/threading.html#condition-objects>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.**

1. In §3, set `judges = 4`. Predict how long the producer is blocked.
2. In §3, set the queue capacity to `1`. Predict the number judged and whether the producer waits more or less.
3. In §3, send one poison pill instead of one per judge. Predict what the program does.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
