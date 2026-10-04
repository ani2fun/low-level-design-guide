---
title: "Locks & Semaphores"
summary: "The explicit locking toolkit beyond synchronized. ReentrantLock with unlock in finally, and the leak when it isn't; tryLock with a timeout so a thread can give up instead of waiting forever; why an idle user must never hold a lock, and the seat hold with an expiry time that replaces it; ReadWriteLock for read-heavy data; and Semaphore for capping how many threads use something at once, from device limits to connection pools. Ends with how monitors, locks, mutexes and semaphores differ. Every example runs in Java and Python, with verified output."
essential: true
---

# Locks & Semaphores — Explicit Control Over Who Runs When

`synchronized` is enough for most code that must run one thread at a time, but it has limits. A thread waiting for a monitor waits as long as it takes; it cannot give up after a timeout. And a monitor always admits one thread, even when several threads only want to read. A booking system needs timeouts and shared reading, and it also needs to limit how many devices or database connections are in use at the same time.

The `java.util.concurrent.locks` package and the `Semaphore` class provide those controls. This lesson applies them to a ticket-booking system. Along the way it replaces a tempting but broken idea, a lock that "expires" when a user goes idle, with the design that real booking systems use.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- `ReentrantLock` is a lock you take and release with explicit method calls, so `unlock()` must go in a `finally` block. In return you get waiting with a timeout (`tryLock`), waiting that can be interrupted, an optional first-come-first-served mode, and condition variables.
- A lock should protect a few lines of code, not a user's whole session. A reservation that lasts minutes should be stored as data with an expiry time.
- A `ReadWriteLock` lets many readers in at the same time. A `Semaphore` lets up to *N* threads in at the same time, and no thread owns it.

</div>

This builds on [Thread Safety & Synchronization](/synapse/low-level-design/multithreading-concurrency/thread-safety-and-synchronization). The Java API details of these classes are in the Java guide's [Concurrency: Coordination](/synapse/programming-languages/java/advanced/concurrency-coordination); this lesson uses them to solve design problems. Every output below was produced by running the code on Java 21 and Python 3.11.

**You'll be able to:** guard a critical section with `ReentrantLock` and explain why `unlock()` belongs in `finally`; use `tryLock(timeout)` to bound a wait; design a seat hold that expires instead of a lock held across user think time; tell when a `ReadWriteLock` pays off; cap concurrent access with a `Semaphore`, failing fast or waiting; choose between a monitor, a `ReentrantLock` and a `Semaphore`.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the lock or semaphore *does*.
2. **A concrete bite** — a specific, runnable failure, shown so the trap is visible.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [`ReentrantLock`: lock, and unlock in `finally`](#1-reentrantlock-lock-and-unlock-in-finally)
2. [`tryLock`: waiting with a limit](#2-trylock-waiting-with-a-limit)
3. [Never hold a lock while a user thinks](#3-never-hold-a-lock-while-a-user-thinks)
4. [`ReadWriteLock`: many readers, one writer](#4-readwritelock-many-readers-one-writer)
5. [`Semaphore`: at most N at a time](#5-semaphore-at-most-n-at-a-time)
6. [Monitor, lock, mutex, semaphore: choosing](#6-monitor-lock-mutex-semaphore-choosing)
7. [Mental-model summary](#7-mental-model-summary)
8. [Gotcha checklist](#8-gotcha-checklist)
9. [Check yourself](#-check-yourself)
10. [Sources](#-sources)

---

## 1. `ReentrantLock`: lock, and unlock in `finally`

`ReentrantLock` does the same job as a `synchronized` block, but as an object with methods you call <abbr title="Java SE 21 API, java.util.concurrent.locks.ReentrantLock">[1]</abbr>. Like a monitor, it is **reentrant** (the thread holding it can lock it again) and **owned** (only the thread that locked it may unlock it). Here, three users try to book one seat:

```java run
import java.util.concurrent.locks.ReentrantLock;

class Show {
    private final ReentrantLock lock = new ReentrantLock();
    private int seatsLeft = 1;

    boolean book(String user) {
        lock.lock();
        try {
            if (seatsLeft == 0) return false;
            seatsLeft--;
            return true;
        } finally {
            lock.unlock();  // runs on every path: return, exception, normal exit
        }
    }
}

public class Main {
    public static void main(String[] args) throws InterruptedException {
        Show show = new Show();
        Thread[] users = new Thread[3];
        for (int i = 0; i < 3; i++) {
            String user = "user-" + (i + 1);
            users[i] = new Thread(() -> System.out.println(user + (show.book(user) ? " booked" : ": sold out")));
            users[i].start();
        }
        for (Thread t : users) t.join();
    }
}
```

```python run
import threading


class Show:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.seats_left = 1

    def book(self, user: str) -> bool:
        self._lock.acquire()
        try:
            if self.seats_left == 0:
                return False
            self.seats_left -= 1
            return True
        finally:
            self._lock.release()  # runs on every path; `with self._lock:` does the same


show = Show()


def attempt(user: str) -> None:
    print(f"{user} booked\n" if show.book(user) else f"{user}: sold out\n", end="")


users = [threading.Thread(target=attempt, args=(f"user-{i}",)) for i in range(1, 4)]
for t in users:
    t.start()
for t in users:
    t.join()
```

**Output** *(illustrative — which user wins varies per run; exactly one always books):*
```
user-1 booked
user-2: sold out
user-3: sold out
```

**Analysis.** One user booked and two found the show sold out. The pattern is always the same: call `lock()`, open a `try`, do the protected work, and call `unlock()` in `finally`. Python's `Lock` follows the same shape with `acquire()` and `release()`, and `with self._lock:` writes that pattern for you.

**Intuition.**
*Mechanism.* A `synchronized` block releases its monitor automatically whenever execution leaves the block, however it leaves. An explicit lock is released only when `unlock()` actually runs. If an exception skips that call, the lock stays held, even after the thread that owns it has ended.

*Concrete bite.* If `unlock()` sits at the end of the method instead of in `finally`, an exception in between (a declined payment, say) skips it. The lock then stays held after the thread that took it has ended. Every later caller waits forever, and nothing in the program can release it. The Java guide [runs that failure](/synapse/programming-languages/java/advanced/concurrency-coordination).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Write `lock.lock(); try { … } finally { lock.unlock(); }` every time, with nothing that can throw between `lock()` and `try`. When you don't need the extra features listed below, prefer `synchronized` (or Python's `with`), because it can never be left locked by mistake.

The cost of an explicit lock is that you must follow this pattern every time. The benefit is the features `synchronized` lacks: waiting with a timeout or waiting that can be interrupted (`tryLock`, `lockInterruptibly`), a **fair** mode that gives the lock to threads in the order they asked for it (`new ReentrantLock(true)`), and several condition variables per lock (`newCondition()`, used in [Producer-Consumer](/synapse/low-level-design/multithreading-concurrency/producer-consumer)).

</div>

---

## 2. `tryLock`: waiting with a limit

A thread waiting for a monitor cannot stop waiting. `tryLock()` returns `false` immediately if another thread holds the lock, and `tryLock(timeout, unit)` waits for at most the given time <abbr title="Java SE 21 API, java.util.concurrent.locks.Lock">[2]</abbr>. Here, Alice takes one second to pay, and Bob is willing to wait half a second:

```java run
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class Main {
    static final ReentrantLock seatLock = new ReentrantLock();

    static void book(String user, long holdMs) {
        try {
            if (!seatLock.tryLock(500, TimeUnit.MILLISECONDS)) {  // wait at most 500 ms
                System.out.println(user + " gave up after 500 ms: try again later");
                return;
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return;
        }
        try {
            System.out.println(user + " has the lock");
            Thread.sleep(holdMs);  // a slow payment
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            seatLock.unlock();
            System.out.println(user + " released the lock");
        }
    }

    public static void main(String[] args) throws InterruptedException {
        Thread alice = new Thread(() -> book("alice", 1_000));
        Thread bob = new Thread(() -> book("bob", 100));
        alice.start();
        Thread.sleep(100);  // bob arrives while alice is paying
        bob.start();
        alice.join();
        bob.join();
    }
}
```

```python run
import threading
import time

seat_lock = threading.Lock()


def book(user: str, hold: float) -> None:
    if not seat_lock.acquire(timeout=0.5):  # wait at most 500 ms
        print(f"{user} gave up after 500 ms: try again later")
        return
    try:
        print(f"{user} has the lock")
        time.sleep(hold)  # a slow payment
    finally:
        seat_lock.release()
        print(f"{user} released the lock")


alice = threading.Thread(target=book, args=("alice", 1.0))
bob = threading.Thread(target=book, args=("bob", 0.1))
alice.start()
time.sleep(0.1)  # bob arrives while alice is paying
bob.start()
alice.join()
bob.join()
```

**Output:**
```
alice has the lock
bob gave up after 500 ms: try again later
alice released the lock
```

**Analysis.** Bob arrived while Alice held the lock. He waited 500 ms, then gave up and printed a message instead of hanging. Alice finished afterwards and released the lock. In Python, `acquire(timeout=0.5)` does the same.

**Intuition.**
*Mechanism.* `tryLock(timeout)` returns `true` if it got the lock, or `false` if it didn't. Only call `unlock()` when it returned `true`: unlocking a lock you don't hold throws `IllegalMonitorStateException`.

*Concrete bite.* With a timeout, the caller can no longer simply wait forever; it has to decide what to do instead: retry, show "this seat is busy, please try again", or fail the request. It is also one of the ways out of [deadlock](/synapse/low-level-design/multithreading-concurrency/deadlock).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** In any code that serves a user, put a time limit on every lock wait with `tryLock(timeout)`, and decide what happens when the wait fails.

The cost is an extra failure path to write and test. The benefit is a system that answers "busy, please try again" under pressure, instead of freezing.

</div>

---

## 3. Never hold a lock while a user thinks

A ticket site lets a user pick a seat, then fill in payment details. Suppose the booking thread locks the seat when it is picked and unlocks it after payment. A user who walks away from the screen then keeps the lock indefinitely, and everyone else waits.

The tempting fix is a lock that "expires": a timer that releases it after a few minutes. That can't work with `ReentrantLock`, because only the thread that owns the lock may unlock it; a timer thread that calls `unlock()` gets an `IllegalMonitorStateException`. A lock with no owner, such as a `Semaphore` or Python's plain `Lock`, *can* be released by a timer, but that is worse. The original thread may still be inside its protected code, and the next user's thread would now be running that code at the same time.

The real problem is the design. A lock should protect a few lines of code for a few microseconds. A reservation that lasts minutes is **data**: record who holds the seat and until when, and use a lock only while changing that record.

```java run
import java.util.HashMap;
import java.util.Map;

// A seat hold is data with an expiry time, not a lock held while the user thinks.
class SeatInventory {
    private record Hold(String user, long expiresAt) {}

    private final Map<String, Hold> holds = new HashMap<>();
    private final Map<String, String> sold = new HashMap<>();
    private final long holdMs;

    SeatInventory(long holdMs) {
        this.holdMs = holdMs;
    }

    // Each method holds the lock for microseconds, never across user think time.
    synchronized String hold(String seat, String user) {
        if (sold.containsKey(seat)) return user + ": " + seat + " is sold";
        Hold h = holds.get(seat);
        long now = System.currentTimeMillis();
        if (h != null && h.expiresAt() > now && !h.user().equals(user)) {
            return user + ": " + seat + " is held by " + h.user();
        }
        holds.put(seat, new Hold(user, now + holdMs));
        return user + ": holding " + seat;
    }

    synchronized String confirm(String seat, String user) {
        Hold h = holds.get(seat);
        if (h == null || !h.user().equals(user) || h.expiresAt() <= System.currentTimeMillis()) {
            return user + ": hold on " + seat + " expired, cannot confirm";
        }
        holds.remove(seat);
        sold.put(seat, user);
        return user + ": confirmed " + seat;
    }
}

public class Main {
    public static void main(String[] args) throws InterruptedException {
        SeatInventory seats = new SeatInventory(300);  // holds last 300 ms in this demo

        System.out.println(seats.hold("A1", "alice"));     // alice picks a seat, then goes idle
        Thread.sleep(100);
        System.out.println(seats.hold("A1", "bob"));       // too soon: alice's hold is live
        Thread.sleep(300);
        System.out.println(seats.hold("A1", "bob"));       // alice's hold has expired
        System.out.println(seats.confirm("A1", "alice"));  // alice comes back too late
        System.out.println(seats.confirm("A1", "bob"));
    }
}
```

```python run
import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Hold:
    user: str
    expires_at: float


# A seat hold is data with an expiry time, not a lock held while the user thinks.
class SeatInventory:
    def __init__(self, hold_seconds: float) -> None:
        self._lock = threading.Lock()
        self._holds: dict[str, Hold] = {}
        self._sold: dict[str, str] = {}
        self._hold_seconds = hold_seconds

    # Each method holds the lock for microseconds, never across user think time.
    def hold(self, seat: str, user: str) -> str:
        with self._lock:
            if seat in self._sold:
                return f"{user}: {seat} is sold"
            h = self._holds.get(seat)
            now = time.monotonic()
            if h and h.expires_at > now and h.user != user:
                return f"{user}: {seat} is held by {h.user}"
            self._holds[seat] = Hold(user, now + self._hold_seconds)
            return f"{user}: holding {seat}"

    def confirm(self, seat: str, user: str) -> str:
        with self._lock:
            h = self._holds.get(seat)
            if h is None or h.user != user or h.expires_at <= time.monotonic():
                return f"{user}: hold on {seat} expired, cannot confirm"
            del self._holds[seat]
            self._sold[seat] = user
            return f"{user}: confirmed {seat}"


seats = SeatInventory(0.3)  # holds last 300 ms in this demo

print(seats.hold("A1", "alice"))     # alice picks a seat, then goes idle
time.sleep(0.1)
print(seats.hold("A1", "bob"))       # too soon: alice's hold is live
time.sleep(0.3)
print(seats.hold("A1", "bob"))       # alice's hold has expired
print(seats.confirm("A1", "alice"))  # alice comes back too late
print(seats.confirm("A1", "bob"))
```

**Output:**
```
alice: holding A1
bob: A1 is held by alice
bob: holding A1
alice: hold on A1 expired, cannot confirm
bob: confirmed A1
```

**Analysis.** Alice held seat A1 and went idle. Bob was refused while her hold was still valid. After it expired, Bob took the seat. When Alice came back, her confirmation was rejected, and Bob's went through. No thread ever waited for a lock longer than the few microseconds each method takes; `synchronized` (or `with self._lock:`) only protects the updates to the maps.

**Intuition.**
*Mechanism.* The expiry time is checked only when someone looks at the hold. No timer needs to fire: an expired hold simply stops counting. A cleanup job can delete old entries later, but the booking logic is correct without it.

*Concrete bite.* Large booking systems work this way. There, the hold is often stored in a database row or in a cache entry with an expiry time, so that it survives restarts and works across many servers.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Hold a lock only while changing shared state. Never hold one while waiting for slow I/O you don't control, or while a user decides what to do. Store long reservations as data with an owner and an expiry time.

The cost is more to design: holds, expiry, and confirmation. The benefit is that no user can freeze the system by walking away.

</div>

---

## 4. `ReadWriteLock`: many readers, one writer

Much shared data is read far more than it is written: prices, configuration, a product catalogue. With a plain lock, readers queue up behind each other even though reading changes nothing. A `ReadWriteLock` has two locks: a **read lock**, which many threads can hold at the same time as long as nobody is writing, and a **write lock**, which only one thread can hold, with no readers <abbr title="Java SE 21 API, java.util.concurrent.locks.ReentrantReadWriteLock">[3]</abbr>. Here are three slow readers, first with a plain lock and then with a read lock:

```java run
import java.util.concurrent.locks.*;

class PriceBoard {
    private final ReadWriteLock rw = new ReentrantReadWriteLock();
    private final Lock plain = new ReentrantLock();
    private double price = 100.0;

    double readWith(Lock lock) throws InterruptedException {
        lock.lock();
        try {
            Thread.sleep(300);  // a slow read, e.g. formatting a big quote
            return price;
        } finally {
            lock.unlock();
        }
    }

    Lock readLock() { return rw.readLock(); }
    Lock plainLock() { return plain; }
}

public class Main {
    static long timeThreeReaders(PriceBoard board, Lock lock) throws InterruptedException {
        long start = System.nanoTime();
        Thread[] readers = new Thread[3];
        for (int i = 0; i < 3; i++) {
            readers[i] = new Thread(() -> {
                try {
                    board.readWith(lock);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
            readers[i].start();
        }
        for (Thread t : readers) t.join();
        return Math.round((System.nanoTime() - start) / 1e8) * 100;
    }

    public static void main(String[] args) throws InterruptedException {
        PriceBoard board = new PriceBoard();
        System.out.println("3 readers, one ReentrantLock:  ~" + timeThreeReaders(board, board.plainLock()) + " ms");
        System.out.println("3 readers, shared read lock:   ~" + timeThreeReaders(board, board.readLock()) + " ms");
    }
}
```

**Output:**
```
3 readers, one ReentrantLock:  ~900 ms
3 readers, shared read lock:   ~300 ms
```

**Analysis.** With one `ReentrantLock`, the three 300 ms reads ran one after another: about 900 ms. With the shared read lock, they ran at the same time: about 300 ms. A writer calling `writeLock().lock()` would wait for all readers to finish, then keep everyone else out while it writes.

Python's standard library has no read-write lock; `threading` only provides locks that admit one thread at a time. You can build one from a `Condition`, but the standard library has no ready-made version, so this section has no Python example.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a `ReadWriteLock` when reads are frequent and slow, and writes are rare. For short reads, a plain lock, or an immutable copy of the data stored in a `volatile` field, is simpler and often faster.

The cost is extra bookkeeping: a read-write lock does more work each time it is taken, and while readers keep arriving, a writer may wait a long time.

</div>

---

## 5. `Semaphore`: at most N at a time

A **semaphore** holds a number of **permits**. `acquire()` takes a permit, waiting if none are left. `release()` gives one back. `tryAcquire()` takes a permit only if one is available right now <abbr title="Java SE 21 API, java.util.concurrent.Semaphore">[4]</abbr>. Here, a premium account allows two devices:

```java run
import java.util.concurrent.Semaphore;

class PremiumAccount {
    private final Semaphore deviceSlots;

    PremiumAccount(int maxDevices) {
        deviceSlots = new Semaphore(maxDevices);
    }

    boolean login(String device) {
        boolean ok = deviceSlots.tryAcquire();  // take a permit if one is free; never wait
        System.out.println(device + (ok ? " logged in" : " refused: device limit reached"));
        return ok;
    }

    void logout(String device) {
        deviceSlots.release();  // give the permit back
        System.out.println(device + " logged out");
    }
}

public class Main {
    public static void main(String[] args) {
        PremiumAccount account = new PremiumAccount(2);
        account.login("phone");
        account.login("laptop");
        account.login("tv");      // a third device
        account.logout("phone");
        account.login("tv");      // now there is a free slot
    }
}
```

```python run
import threading


class PremiumAccount:
    def __init__(self, max_devices: int) -> None:
        self._device_slots = threading.Semaphore(max_devices)

    def login(self, device: str) -> bool:
        ok = self._device_slots.acquire(blocking=False)  # take a permit if one is free; never wait
        print(f"{device} logged in" if ok else f"{device} refused: device limit reached")
        return ok

    def logout(self, device: str) -> None:
        self._device_slots.release()  # give the permit back
        print(f"{device} logged out")


account = PremiumAccount(2)
account.login("phone")
account.login("laptop")
account.login("tv")      # a third device
account.logout("phone")
account.login("tv")      # now there is a free slot
```

**Output:**
```
phone logged in
laptop logged in
tv refused: device limit reached
phone logged out
tv logged in
```

**Analysis.** There were two permits, so two devices got in. The TV was refused at once by `tryAcquire()`, without waiting. When the phone logged out and released its permit, the TV got in. In Python, `acquire(blocking=False)` does the same as `tryAcquire()`.

The waiting form, `acquire()`, limits how many threads use something at once. Here, eight threads run queries against a database that allows two connections:

```java run
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class Main {
    static final Semaphore connections = new Semaphore(2);  // the database allows 2 connections
    static final AtomicInteger inUse = new AtomicInteger();
    static final AtomicInteger peak = new AtomicInteger();

    static void query(int id) throws InterruptedException {
        connections.acquire();  // wait for a free connection
        try {
            peak.accumulateAndGet(inUse.incrementAndGet(), Math::max);
            Thread.sleep(100);  // run the query
            inUse.decrementAndGet();
        } finally {
            connections.release();
        }
    }

    public static void main(String[] args) throws Exception {
        try (ExecutorService pool = Executors.newFixedThreadPool(8)) {
            for (int i = 0; i < 8; i++) {
                int id = i;
                pool.submit(() -> { query(id); return null; });
            }
        }
        System.out.println("8 queries on 8 threads; most connections in use at once: " + peak.get());
    }
}
```

```python run
import threading
import time
from concurrent.futures import ThreadPoolExecutor

connections = threading.Semaphore(2)  # the database allows 2 connections
lock = threading.Lock()
in_use = 0
peak = 0


def query(qid: int) -> None:
    global in_use, peak
    with connections:  # wait for a free connection
        with lock:
            in_use += 1
            peak = max(peak, in_use)
        time.sleep(0.1)  # run the query
        with lock:
            in_use -= 1


with ThreadPoolExecutor(max_workers=8) as pool:
    for i in range(8):
        pool.submit(query, i)

print("8 queries on 8 threads; most connections in use at once:", peak)
```

**Output:**
```
8 queries on 8 threads; most connections in use at once: 2
```

**Analysis.** Eight threads were ready to run, but no more than two ever held a connection at the same time. The other six waited in `acquire()` until a permit was returned. This protects a limited resource however many threads there are, for example with [virtual threads](/synapse/low-level-design/multithreading-concurrency/thread-pools-and-executors).

**Intuition.**
*Mechanism.* A semaphore is a counter that threads can wait on. It has **no owner**: any thread may call `release()`, and nothing checks that it acquired a permit first. That makes it useful for passing permits between threads, and dangerous when a `release()` is missed or called twice.

*Concrete bite.* A skipped `release()` loses a permit forever; after enough of them, nobody gets in at all. A `release()` without a matching acquire *adds* a permit, quietly raising the limit. Put `release()` in a `finally` block, and only on the code path where the acquire succeeded. In Python, `threading.BoundedSemaphore` turns an extra release into a `ValueError` instead of a silent extra permit <abbr title="Python 3 documentation, threading, Semaphore objects">[5]</abbr>.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use a `Semaphore` to limit how many threads use something at the same time: database connections, device sessions, calls to an API with a rate limit. Use `tryAcquire` to fail immediately, and `acquire` (or `tryAcquire(timeout)`) to wait.

The cost is that a semaphore can't tell a correct `release()` from a buggy one. Keep the acquire and the release in the same method, in a `try`/`finally`.

</div>

---

## 6. Monitor, lock, mutex, semaphore: choosing

**Mutex** (short for mutual exclusion lock) is the general name for a lock that one thread holds at a time and that only the same thread may release. Java has two: the monitor behind `synchronized`, and `ReentrantLock`. A semaphore with one permit also lets in one thread at a time, but it is not a mutex, because nobody owns it.

| | Monitor (`synchronized`) | `ReentrantLock` | `ReadWriteLock` | `Semaphore` |
|---|---|---|---|---|
| Threads inside at once | 1 | 1 | many readers, or 1 writer | up to N |
| Owner | the locking thread | the locking thread | the locking thread | none |
| Reentrant | yes | yes | yes | no |
| Released automatically | yes, on leaving the block | no: `unlock()` in `finally` | no: `unlock()` in `finally` | no: `release()` in `finally` |
| Timed or non-blocking attempt | no | `tryLock(…)` | `tryLock(…)` | `tryAcquire(…)` |
| Fair mode | no | optional | optional | optional |
| Waiting for a condition | `wait`/`notify` | `Condition` objects | `Condition` (write lock) | — |
| Typical use | most critical sections | timeouts, fairness, several conditions | read-heavy shared data | capping concurrent use |

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Start with `synchronized`. Switch to `ReentrantLock` when you need a timeout, interruptible waiting, fairness or several conditions; to a `ReadWriteLock` when slow reads make up most of the work; and to a `Semaphore` when the limit is N threads rather than 1.

Each step adds more ways to get the release wrong. Take it only when you need the feature it brings.

</div>

---

## 7. Mental-model summary

| Principle | Consequence |
|---|---|
| `ReentrantLock` is released only by `unlock()` | `unlock()` in `finally`, or a thrown exception leaks the lock forever |
| `tryLock(timeout)` bounds a wait | The caller decides what to do when the lock is busy |
| Only the owner may unlock a `ReentrantLock` | A timer cannot release it; expiring locks are the wrong design |
| Long reservations are data with an expiry time | Locks guard microseconds of state change, never user think time |
| A read lock is shared; a write lock is exclusive | Slow, frequent reads overlap; writes still exclude everyone |
| A semaphore counts permits and has no owner | Caps concurrency at N; a missed or extra `release()` changes the limit |
| A mutex has an owner; a semaphore does not | A one-permit semaphore excludes, but anyone can release it |

## 8. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

| Symptom | Likely cause | Fix |
|---|---|---|
| Every thread waits on a lock nobody seems to hold | an exception skipped `unlock()`; the dead owner still holds it | `unlock()` in `finally` |
| `IllegalMonitorStateException` from `unlock()` | the thread doesn't hold the lock (the `tryLock` failed, or another thread locked it) | unlock only on the path where you acquired |
| Users wait minutes for a seat someone abandoned | a lock held across user think time | a hold with an expiry time, guarded by a short lock |
| A request hangs on a lock | an unbounded `lock()` | `tryLock(timeout)` with a failure path |
| The `ReadWriteLock` made things slower | reads are short, or writes are frequent | a plain lock, or an immutable snapshot |
| More users get in than the limit allows | an extra `release()` added permits | pair each `release()` with a successful acquire |
| Fewer and fewer users get in over time | a missed `release()` leaked permits | `release()` in `finally` |
| Python: the same thread hangs on a lock it holds | `threading.Lock` is not reentrant | `threading.RLock` |

</div>

---

## ✅ Check yourself

One check per objective. Answer before you open anything.

```quiz
{"prompt": "lock.lock(); doWork(); lock.unlock(); — doWork() throws. What state is the lock in?", "options": ["Still held, with no one left to release it", "Released automatically", "Released when the garbage collector runs"], "answer": "Still held, with no one left to release it"}
```

```quiz
{"prompt": "tryLock(500, MILLISECONDS) is called while another thread holds the lock for 2 seconds. What happens?", "options": ["It returns false after about 500 ms", "It waits 2 seconds and returns true", "It throws IllegalMonitorStateException"], "answer": "It returns false after about 500 ms"}
```

```quiz
{"prompt": "A user picks a seat and may take minutes to pay. What should stop others from taking the seat meanwhile?", "options": ["A hold record with an expiry time, changed under a short lock", "A ReentrantLock held until payment completes", "A synchronized method that sleeps until payment arrives"], "answer": "A hold record with an expiry time, changed under a short lock"}
```

```quiz
{"prompt": "Three threads each hold a ReadWriteLock's read lock for 300 ms, starting together. About how long until all three finish?", "options": ["300 ms", "900 ms", "600 ms"], "answer": "300 ms"}
```

```quiz
{"prompt": "new Semaphore(2): three threads call tryAcquire() and none has released. How many get a permit?", "options": ["2", "3", "1"], "answer": "2"}
```

```quiz
{"prompt": "You need at most 5 concurrent calls to a rate-limited API, from 200 threads. Which tool fits?", "options": ["Semaphore with 5 permits", "ReentrantLock", "ReadWriteLock"], "answer": "Semaphore with 5 permits"}
```

<details>
<summary>The 🧪 box below: Bob's timeout raised to 1.5 s; a semaphore that is released twice; and a hold duration of 50 ms.</summary>

1. Alice holds the lock for 1 s, and Bob arrives at 100 ms, so a 1.5 s wait is long enough. Bob gets the lock at about 1 s, as soon as Alice releases it.
2. The second `release()` adds a permit nobody acquired, so the TV and the tablet both get in and only the watch is refused. Three devices (laptop, TV, tablet) are now logged in, although the limit is two. The semaphore never checks which thread acquired a permit. Python's plain `Semaphore` does the same; `BoundedSemaphore` raises `ValueError` on the extra release.
3. With 50 ms holds, Alice's hold has already expired when Bob asks at 100 ms, so Bob's first request succeeds: `bob: holding A1`.

</details>

---

## 📚 Sources

1. `java.util.concurrent.locks.ReentrantLock`, Java SE 21 API — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/ReentrantLock.html>
2. `java.util.concurrent.locks.Lock`, Java SE 21 API (`tryLock`, `lockInterruptibly`, `newCondition`) — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/Lock.html>
3. `java.util.concurrent.locks.ReentrantReadWriteLock`, Java SE 21 API — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/locks/ReentrantReadWriteLock.html>
4. `java.util.concurrent.Semaphore`, Java SE 21 API — <https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Semaphore.html>
5. Python 3 documentation, `threading` — Lock, RLock and Semaphore objects — <https://docs.python.org/3/library/threading.html>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.**

1. In section 2, raise Bob's timeout to 1,500 ms. Predict what Bob prints, and roughly when.
2. In section 5, call `account.logout("phone")` twice in a row, then log in `"tv"`, `"tablet"` and `"watch"`. Predict which are refused.
3. In section 3, make holds last 50 ms instead of 300 ms. Predict Bob's first answer.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
