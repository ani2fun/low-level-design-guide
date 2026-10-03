---
title: "Errors, Generics & Resources in Design"
summary: "Three language features seen as design decisions. Exceptions are part of a class's contract: a failure reported by an ignorable return value gets lost, while a domain exception says what went wrong in business terms. Generics turn one component, such as a repository, into a type-safe one for every entity. And every resource and long-lived reference needs an owner, or files stay open and memory leaks. The Java language rules live in the Java guide; every example here runs in Java and Python, with verified output."
essential: true
---

# Errors, Generics & Resources in Design — Contracts, Reuse and Ownership

Exceptions, generics, file handling and garbage collection are usually taught as language features: how to write `try`, what the angle brackets in `List<String>` mean. Those language rules are taught in the Java guide: [Exceptions](/synapse/programming-languages/java/robust-oop/exceptions), [Generics](/synapse/programming-languages/java/core-libraries/generics), [I/O, Files & NIO.2](/synapse/programming-languages/java/advanced/io-files-and-nio2) and [References, Equality & the Object Model](/synapse/programming-languages/java/classes-and-objects/references-equality-and-the-object-model).

This lesson asks the design questions those features help answer. How should a class tell the code that calls it that something went wrong? How do you write one component that works for many types of data? Which object is responsible for closing a file, or for letting go of an object it no longer needs?

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- **Errors are part of a class's contract.** If the calling code can ignore a failure, sooner or later it will. Report failures with exceptions named in the language of the business.
- **Generics** let one component work with many types, with the compiler checking each use.
- **Every resource, and every reference that lives a long time, needs an owner**: one object that is responsible for closing or releasing it.

</div>

This builds on [Abstraction & Interfaces](/synapse/low-level-design/oop/abstraction-interfaces-static-members-inner-classes). Every output below was produced by running the code on Java 21 and Python 3.11.

**You'll be able to:** design how a class reports failure, and choose between returning a value and throwing a domain exception; write a generic component and say what the compiler checks for you; name the owner of each resource in a design, and spot references that keep objects alive too long.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what the design does to the code that uses it.
2. **A concrete bite** — a specific situation where the design choice pays off or hurts.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [Errors are part of the contract](#1-errors-are-part-of-the-contract)
2. [Generics: one component, many types](#2-generics-one-component-many-types)
3. [Resources and references need an owner](#3-resources-and-references-need-an-owner)
4. [Mental-model summary](#4-mental-model-summary)
5. [Gotcha checklist](#5-gotcha-checklist)
6. [Check yourself](#-check-yourself)
7. [Sources](#-sources)

---

## 1. Errors are part of the contract

Here, a wallet reports a failed payment by returning `false`, and the booking code doesn't check the result:

```java run
// ⚠️ ANTI-PATTERN — failure reported by a return value the caller can ignore. Do not copy it.
class Wallet {
    private long balance = 100;

    boolean pay(long amount) {
        if (amount > balance) return false;
        balance -= amount;
        return true;
    }
}

public class Main {
    public static void main(String[] args) {
        Wallet wallet = new Wallet();
        wallet.pay(250);  // the false is dropped on the floor
        System.out.println("ride booked and confirmed to the driver");  // nobody paid
    }
}
```

```python run
# ⚠️ ANTI-PATTERN — failure reported by a return value the caller can ignore. Do not copy it.
class Wallet:
    def __init__(self) -> None:
        self._balance = 100

    def pay(self, amount: int) -> bool:
        if amount > self._balance:
            return False
        self._balance -= amount
        return True


wallet = Wallet()
wallet.pay(250)  # the False is dropped on the floor
print("ride booked and confirmed to the driver")  # nobody paid
```

**Output:**
```
ride booked and confirmed to the driver
```

**Analysis.** The payment failed, but the ride was confirmed anyway. The `false` reported the failure, but nothing forced the calling code to look at it. With a return value, every caller has to remember to check; nothing happens if one forgets.

A **domain exception** (an exception named after a business problem) cannot be ignored silently. Either the calling code handles it, or it travels up the call stack and stops the operation:

```java run
// A domain exception says what went wrong in the language of the business.
class InsufficientFundsException extends RuntimeException {
    final long shortBy;

    InsufficientFundsException(long balance, long amount) {
        super("need " + amount + ", have " + balance);
        this.shortBy = amount - balance;
    }
}

class Wallet {
    private long balance = 100;

    void pay(long amount) {
        if (amount > balance) throw new InsufficientFundsException(balance, amount);
        balance -= amount;
    }
}

public class Main {
    public static void main(String[] args) {
        Wallet wallet = new Wallet();
        try {
            wallet.pay(250);
            System.out.println("ride booked and confirmed to the driver");
        } catch (InsufficientFundsException e) {
            System.out.println("payment failed: " + e.getMessage() + "; ask the rider to top up " + e.shortBy);
        }
    }
}
```

```python run
# A domain exception says what went wrong in the language of the business.
class InsufficientFundsError(Exception):
    def __init__(self, balance: int, amount: int) -> None:
        super().__init__(f"need {amount}, have {balance}")
        self.short_by = amount - balance


class Wallet:
    def __init__(self) -> None:
        self._balance = 100

    def pay(self, amount: int) -> None:
        if amount > self._balance:
            raise InsufficientFundsError(self._balance, amount)
        self._balance -= amount


wallet = Wallet()
try:
    wallet.pay(250)
    print("ride booked and confirmed to the driver")
except InsufficientFundsError as e:
    print(f"payment failed: {e}; ask the rider to top up {e.short_by}")
```

**Output:**
```
payment failed: need 250, have 100; ask the rider to top up 150
```

**Analysis.** The booking stopped before the confirmation line, and the `catch` block had what it needed to recover: a message, and how much money was missing. The exception's name, `InsufficientFundsException`, describes the problem in business terms, so the calling code can handle *this* failure specifically, without catching every `RuntimeException`.

**Intuition.**
*Mechanism.* An exception jumps out of the normal flow of the program until some calling method catches it. Code that forgets to handle it gets a visible failure, not a silently wrong result. Java's **checked** exceptions go further: the compiler makes every calling method either catch them or declare that it throws them <abbr title="The Java Language Specification, Java SE 21, §11.2 Compile-Time Checking of Exceptions">[1]</abbr>. The language details, such as checked versus unchecked exceptions and `try`/`catch`/`finally`, are in the Java guide's [Exceptions](/synapse/programming-languages/java/robust-oop/exceptions).

*Concrete bite.* Three common designs lose errors:

- **Swallowing the exception**: `catch (Exception e) {}` turns a failure into a silent success.
- **Exposing the layer below**: a `PaymentService` that throws `SQLException` forces the code that calls it to know about its database. Catch the `SQLException` and throw a domain exception instead, passing the original as its cause.
- **Returning `null` for "not found"**: every caller must remember to check for `null`. Return `Optional<T>` instead, or throw a domain exception if a missing value is an error.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Treat the ways a method can fail as part of its signature. Use a domain exception for a failure the caller must not miss. Use `Optional` (or a result type) when "no value" is a normal outcome. Convert lower-level exceptions into domain exceptions where one layer calls another. Never swallow an exception.

The cost is designing a set of exception classes, and deciding where each one is caught. Retries, fallbacks and circuit breakers build on this in [Dependency Injection & Error Handling](/synapse/low-level-design/best-practices/dependency-injection-and-error-handling).

</div>

---

## 2. Generics: one component, many types

A repository stores objects by their id. Without generics, you would write `UserRepository`, `OrderRepository` and so on, all nearly identical, or a single repository of `Object` whose results callers must cast. With generics, one class works for every type of object, and the compiler checks each use:

```java run
import java.util.*;

record User(String id, String name) {}
record Order(Long id, String item) {}

// One implementation, reused for every entity type, checked by the compiler.
class InMemoryRepository<T, ID> {
    private final Map<ID, T> rows = new LinkedHashMap<>();
    private final java.util.function.Function<T, ID> idOf;

    InMemoryRepository(java.util.function.Function<T, ID> idOf) {
        this.idOf = idOf;
    }

    void save(T entity) { rows.put(idOf.apply(entity), entity); }
    Optional<T> findById(ID id) { return Optional.ofNullable(rows.get(id)); }
    int count() { return rows.size(); }
}

public class Main {
    public static void main(String[] args) {
        InMemoryRepository<User, String> users = new InMemoryRepository<>(User::id);
        InMemoryRepository<Order, Long> orders = new InMemoryRepository<>(Order::id);

        users.save(new User("u1", "Ada"));
        orders.save(new Order(1001L, "keyboard"));
        // users.save(new Order(1002L, "mouse"));  // does not compile: an Order is not a User

        System.out.println(users.findById("u1").map(User::name).orElse("none"));
        System.out.println(orders.findById(1001L).map(Order::item).orElse("none"));
        System.out.println("users: " + users.count() + ", orders: " + orders.count());
    }
}
```

```python run
from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


@dataclass(frozen=True)
class User:
    id: str
    name: str


@dataclass(frozen=True)
class Order:
    id: int
    item: str


# One implementation, reused for every entity type. A type checker such as mypy
# flags users.save(Order(...)); Python itself does not check at run time.
class InMemoryRepository(Generic[T, ID]):
    def __init__(self, id_of: Callable[[T], ID]) -> None:
        self._rows: dict[ID, T] = {}
        self._id_of = id_of

    def save(self, entity: T) -> None:
        self._rows[self._id_of(entity)] = entity

    def find_by_id(self, entity_id: ID) -> Optional[T]:
        return self._rows.get(entity_id)

    def count(self) -> int:
        return len(self._rows)


users: InMemoryRepository[User, str] = InMemoryRepository(lambda u: u.id)
orders: InMemoryRepository[Order, int] = InMemoryRepository(lambda o: o.id)

users.save(User("u1", "Ada"))
orders.save(Order(1001, "keyboard"))

print(users.find_by_id("u1").name)
print(orders.find_by_id(1001).item)
print(f"users: {users.count()}, orders: {orders.count()}")
```

**Output:**
```
Ada
keyboard
users: 1, orders: 1
```

**Analysis.** The same `InMemoryRepository` class stored users with `String` ids and orders with `Long` ids. `users.findById("u1")` returned a `User`, with no cast needed. In Java, saving an `Order` into the user repository is a compile-time error. Python records the same type parameters for type-checking tools such as mypy, but does not check them while the program runs.

**Intuition.**
*Mechanism.* A type parameter (`T`, `ID`) is a placeholder that each use of the class fills in. The compiler checks every call against the types filled in, and then removes them: at run time there is just one `InMemoryRepository` class <abbr title="The Java Language Specification, Java SE 21, §4.6 Type Erasure">[2]</abbr>. Bounds (`<T extends Comparable<T>>`) and wildcards (`List<? extends Shape>`) are covered in the Java guide's [Generics](/synapse/programming-languages/java/core-libraries/generics).

*Concrete bite.* With a repository of `Object`, a mistake like saving an order as a user compiles without complaint. It fails later, far from where it was made, with a `ClassCastException` when some other code casts what it reads back. Generics move that failure to the line that caused it, and to compile time.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** When the same logic works for many types (storage, caching, queues, splitting results into pages), write it once with type parameters, rather than once for each type or once for `Object`.

The cost is code that is more abstract and harder to read. Don't make a class generic until a second type needs it.

</div>

---

## 3. Resources and references need an owner

Two kinds of things last longer than a single method call, and must be released on purpose.

**Resources**: files, network connections, database connections, locks. The operating system, or a pool, only hands out a limited number of them. In a design, each resource needs exactly one **owner**: the object that opened it, and that must close it:

- When a resource is used inside one method, Java's `try`-with-resources (Python's `with`) closes it however the method ends, including by an exception <abbr title="The Java Language Specification, Java SE 21, §14.20.3 try-with-resources">[3]</abbr>.
- When an object keeps a resource open for its whole lifetime (a `FileLogger` holding an open file), that object should implement `AutoCloseable` (in Python, `__enter__` and `__exit__`), and *its* owner must close it.
- A method that receives a resource as a parameter does not own it and must not close it.

**References**: an object stays in memory for as long as something still in use refers to it, because the garbage collector only frees objects that nothing can reach. So in Java, a "memory leak" is a reference that is kept after the object is no longer needed. The Java guide's [References, Equality & the Object Model, section 6](/synapse/programming-languages/java/classes-and-objects/references-equality-and-the-object-model) shows when an object becomes unreachable. Common causes of leaks in designs:

| Leak | Why the objects stay alive | Fix |
|---|---|---|
| A cache with no size limit | the map refers to every entry forever | limit its size, and remove old entries (least recently used, or after a time limit) |
| Listeners that are never removed | the event source's list refers to every listener | unregister them when done; give each subscription an owner |
| `static` collections | a static field lives as long as the class | avoid static fields that change ([Abstraction & Interfaces, section 4](/synapse/low-level-design/oop/abstraction-interfaces-static-members-inner-classes)) |
| Long-lived objects holding short-lived ones | a session refers to every request it handled | store only ids, or copy just the data you need |

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** For every resource, and every collection that grows, name its owner in the design and say when it is released. Open and close each resource in the same object, and give every cache a size limit.

The cost is deciding how long things live before you write the code. Leaks discovered in production cost much more.

</div>

---

## 4. Mental-model summary

| Principle | Consequence |
|---|---|
| A failure reported only by a return value gets ignored | Use exceptions for failures the caller must not miss |
| Domain exceptions name failures in business terms | Calling code can handle *this* failure, with the details it needs |
| Convert exceptions where one layer calls another | Calling code doesn't depend on your database or HTTP library |
| Use `Optional` when "no value" is normal; never swallow exceptions | No `null` checks to forget, and no silent successes |
| Generics: one component, checked by the compiler for each type | No copies for each type, no casts, and mistakes caught at compile time |
| Java removes type parameters after compiling; Python doesn't check them at run time | The checking happens in the compiler, or in a type-checking tool |
| Every resource has one owner that closes it | `try`-with-resources / `with`; long-lived holders are `AutoCloseable` |
| An object stays in memory as long as something refers to it | Caches without limits, forgotten listeners and static collections leak memory |

## 5. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

| Symptom | Likely cause | Fix |
|---|---|---|
| An operation "succeeded", but its effect never happened | a `false` or error code was ignored, or an exception was swallowed | throw a domain exception; never catch an exception and ignore it |
| Callers catch `SQLException` in business code | a lower layer's exception leaked through | catch it at the boundary; throw a domain exception with the cause |
| `NullPointerException` far from the lookup that failed | `null` returned for "not found" | `Optional<T>`, or a domain exception |
| `ClassCastException` reading from a collection | an `Object`-typed or raw collection | type parameters |
| "Too many open files" after hours of running | a resource without an owner that closes it | `try`-with-resources; `AutoCloseable` owners |
| Memory grows steadily, then `OutOfMemoryError` | an unbounded cache, listener list or static collection | bound it, evict, unregister |

</div>

---

## ✅ Check yourself

One check per objective. Answer before you open anything.

```quiz
{"prompt": "A transfer method returns false when the source account has too little money. What is the main design risk?", "options": ["A caller can ignore the false and carry on as if it succeeded", "Booleans are slower than exceptions", "The method cannot be tested"], "answer": "A caller can ignore the false and carry on as if it succeeded"}
```

```quiz
{"prompt": "InMemoryRepository<User, String> users exists. What happens at users.save(new Order(1L, \"mouse\")) in Java?", "options": ["A compile-time error", "A ClassCastException at run time", "It is saved, keyed by the order's id"], "answer": "A compile-time error"}
```

```quiz
{"prompt": "A ReportWriter opens a file in its constructor and writes to it from several methods. Who should close the file?", "options": ["ReportWriter, in close(), with its own owner calling close() via try-with-resources", "Each method that writes to it", "The garbage collector"], "answer": "ReportWriter, in close(), with its own owner calling close() via try-with-resources"}
```

<details>
<summary>A <code>UserService</code> calls a <code>UserDao</code> that throws <code>SQLException</code>, and returns <code>null</code> when a user is missing. Redesign its error contract.</summary>

Inside `UserService`, catch `SQLException` and throw a domain exception such as `UserStoreUnavailableException`, passing the original exception as its cause so the full stack trace is kept. Return `Optional<User>` from `findById`, because a missing user is a normal outcome, not an error. Code that uses `UserService` then deals only with ideas about users (an empty `Optional`, or a user store that is unavailable) and never with JDBC.

</details>

---

## 📚 Sources

1. *The Java Language Specification, Java SE 21*, §11.2 "Compile-Time Checking of Exceptions" — <https://docs.oracle.com/javase/specs/jls/se21/html/jls-11.html#jls-11.2>
2. *The Java Language Specification, Java SE 21*, §4.6 "Type Erasure" — <https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html#jls-4.6>
3. *The Java Language Specification, Java SE 21*, §14.20.3 "try-with-resources" — <https://docs.oracle.com/javase/specs/jls/se21/html/jls-14.html#jls-14.20.3>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.**

1. In section 1, remove the `try`/`catch` around `wallet.pay(250)`. Predict what is printed, and whether the confirmation line appears.
2. In section 2, uncomment `users.save(new Order(1002L, "mouse"))`. Predict the compiler's complaint.
3. In the Python version from section 2, add `users.save(Order(1002, "mouse"))` and run it. Predict what happens, then run `mypy` on it if you have it.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
