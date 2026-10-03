---
title: "Errors, Generics & Resources in Design"
summary: "Three language features seen as design decisions. Exceptions are part of a class's contract: a failure reported by an ignorable return value gets lost, while a domain exception says what went wrong in business terms. Generics turn one component, such as a repository, into a type-safe one for every entity. And every resource and long-lived reference needs an owner, or files stay open and memory leaks. The Java language rules live in the Java guide; every example here runs in Java and Python, with verified output."
essential: true
---

# Errors, Generics & Resources in Design — Contracts, Reuse and Ownership

Exceptions, generics, file handling and garbage collection are usually taught as language features: the syntax of `try`, the angle brackets of `List<String>`. Those rules are in the Java guide: [Exceptions](/synapse/programming-languages/java/robust-oop/exceptions), [Generics](/synapse/programming-languages/java/core-libraries/generics), [I/O, Files & NIO.2](/synapse/programming-languages/java/advanced/io-files-and-nio2) and [References, Equality & the Object Model](/synapse/programming-languages/java/classes-and-objects/references-equality-and-the-object-model).

This lesson asks the design questions those features answer. How does a class tell its callers that something went wrong? How do you write one component that works for many types? Who is responsible for closing a file, or for letting go of an object?

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- **Errors are part of the contract.** A failure the caller can ignore will be ignored. Signal failures with exceptions named in the domain's language.
- **Generics** let one component serve many types, with the compiler checking each use.
- **Every resource and every long-lived reference needs an owner**: one object responsible for closing or releasing it.

</div>

This builds on [Abstraction & Interfaces](/synapse/low-level-design/oop/abstraction-interfaces-static-members-inner-classes). Every output below was produced by running the code on Java 21 and Python 3.11.

**You'll be able to:** design how a class reports failure, and choose between a return value and a domain exception; write a generic component and say what the compiler checks for you; name the owner of each resource in a design, and spot references that keep objects alive too long.

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

A wallet reports a failed payment by returning `false`. The booking code doesn't check:

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

**Analysis.** The payment failed, and the ride was confirmed anyway. The `false` carried the failure, and nothing forced anyone to look at it. A return code is an error signal that is opt-in for every caller.

A **domain exception** cannot be dropped silently. Either the caller handles it, or it propagates and stops the operation:

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

**Analysis.** The booking stopped before the confirmation line, and the handler had what it needed to recover: a message, and how much was missing. The exception's name, `InsufficientFundsException`, says what went wrong in the business's terms, so the caller can handle *this* failure without catching every `RuntimeException`.

**Intuition.**
*Mechanism.* An exception transfers control out of the normal path until some caller catches it. A caller who forgets to handle it gets a visible failure, not a silent wrong result. Java's **checked** exceptions go further: the compiler makes every caller either catch them or declare them <abbr title="The Java Language Specification, Java SE 21, §11.2 Compile-Time Checking of Exceptions">[1]</abbr>. The mechanics, checked versus unchecked and `try`/`catch`/`finally`, are in the Java guide's [Exceptions](/synapse/programming-languages/java/robust-oop/exceptions).

*Concrete bite.* Three common designs lose errors:

- **Swallowing**: `catch (Exception e) {}` turns a failure into silent success.
- **Leaking the layer below**: a `PaymentService` that throws `SQLException` forces callers to know about its database. Catch it and throw a domain exception, keeping the original as the cause.
- **`null` for "not found"**: every caller must remember to check. Return `Optional<T>`, or throw a domain exception if absence is an error.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Treat a method's failures as part of its signature. Use a domain exception for a failure the caller must not miss; use `Optional` or a result type when "no value" is a normal outcome; translate lower-level exceptions at layer boundaries; never swallow one.

The cost is designing an exception hierarchy and deciding where to catch. Retries, fallbacks and circuit breakers build on this in [Dependency Injection & Error Handling](/synapse/low-level-design/best-practices/dependency-injection-and-error-handling).

</div>

---

## 2. Generics: one component, many types

A repository stores entities by id. Without generics you would write `UserRepository`, `OrderRepository` and so on, all the same, or one repository of `Object` that callers must cast. With generics, one class serves every entity type, and the compiler checks each use:

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

**Analysis.** The same `InMemoryRepository` stored users keyed by `String` and orders keyed by `Long`. `users.findById("u1")` returned a `User`, with no cast. Saving an `Order` into the user repository is a compile-time error in Java. Python records the same type parameters for type checkers such as mypy, but does not enforce them when the program runs.

**Intuition.**
*Mechanism.* A type parameter (`T`, `ID`) is a placeholder that each use fills in. The compiler checks every call against the filled-in types, then erases them: at run time there is one `InMemoryRepository` class <abbr title="The Java Language Specification, Java SE 21, §4.6 Type Erasure">[2]</abbr>. Bounds (`<T extends Comparable<T>>`) and wildcards (`List<? extends Shape>`) are covered in the Java guide's [Generics](/synapse/programming-languages/java/core-libraries/generics).

*Concrete bite.* A repository of `Object` compiles a mistake like saving an order as a user, and fails later, far from the cause, with a `ClassCastException` when someone casts what they read back. Generics move that failure to the line that caused it, at compile time.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** When the same logic works for many types (storage, caching, queues, pagination, results), write it once with type parameters rather than once per type or once for `Object`.

The cost is more abstract code to read. Don't make a class generic until a second type needs it.

</div>

---

## 3. Resources and references need an owner

Two kinds of thing outlive a single method call and must be let go of deliberately.

**Resources**: files, sockets, database connections, locks. The operating system or a pool hands out a limited number. In a design, each resource needs exactly one **owner**, the object that opened it and must close it:

- Inside one method, Java's `try`-with-resources (Python's `with`) closes the resource on every path, exceptions included <abbr title="The Java Language Specification, Java SE 21, §14.20.3 try-with-resources">[3]</abbr>.
- When an object holds a resource for its lifetime (a `FileLogger` holding an open file), the object should implement `AutoCloseable` (Python: `__enter__`/`__exit__`), and *its* owner must close it.
- A method that receives a resource as a parameter does not own it and must not close it.

**References**: an object stays in memory for as long as something reachable refers to it; the garbage collector frees only unreachable objects. So in Java, a "memory leak" is a reference that outlives its usefulness. The Java guide's [References, Equality & the Object Model, §6](/synapse/programming-languages/java/classes-and-objects/references-equality-and-the-object-model) shows when an object becomes unreachable. Common leaks in designs:

| Leak | Why the objects stay alive | Fix |
|---|---|---|
| A cache with no limit | the map refers to every entry forever | bound it, and evict (LRU, time-to-live) |
| Listeners never removed | the event source's list refers to every listener | unregister on close; give subscriptions an owner |
| `static` collections | a static field lives as long as the class | avoid static mutable state ([Abstraction & Interfaces, §4](/synapse/low-level-design/oop/abstraction-interfaces-static-members-inner-classes)) |
| Long-lived objects holding short-lived ones | a session refers to every request it handled | keep only ids, or copy what you need |

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** For every resource and every collection that grows, name its owner in the design and say when it is released. Open and close in the same object; bound every cache.

The cost is deciding lifetimes up front. Leaks found in production cost much more.

</div>

---

## 4. Mental-model summary

| Principle | Consequence |
|---|---|
| A failure reported by an ignorable return value gets ignored | Use exceptions for failures callers must not miss |
| Domain exceptions name failures in business terms | Callers handle *this* failure, with the details they need |
| Translate exceptions at layer boundaries | Callers don't depend on your database or HTTP library |
| `Optional` for normal absence; never swallow exceptions | No `null` checks to forget; no silent successes |
| Generics: one component, compiler-checked for each type | No per-type copies, no casts, mistakes caught at compile time |
| Java erases type parameters; Python doesn't enforce them at run time | The checking happens in the compiler or type checker |
| Every resource has one owner that closes it | `try`-with-resources / `with`; long-lived holders are `AutoCloseable` |
| An object lives as long as something refers to it | Unbounded caches, forgotten listeners and static collections leak |

## 5. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

| Symptom | Likely cause | Fix |
|---|---|---|
| An operation "succeeded" but its effect never happened | a `false` or error code was ignored, or an exception swallowed | throw a domain exception; never catch and ignore |
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

At the `UserService` boundary, catch `SQLException` and throw a domain exception such as `UserStoreUnavailableException`, passing the original as its cause so the stack trace survives. Return `Optional<User>` from `findById`, since a missing user is a normal outcome, not an error. Callers then deal only with user concepts: an empty `Optional` or a store that is unavailable, never JDBC.

</details>

---

## 📚 Sources

1. *The Java Language Specification, Java SE 21*, §11.2 "Compile-Time Checking of Exceptions" — <https://docs.oracle.com/javase/specs/jls/se21/html/jls-11.html#jls-11.2>
2. *The Java Language Specification, Java SE 21*, §4.6 "Type Erasure" — <https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html#jls-4.6>
3. *The Java Language Specification, Java SE 21*, §14.20.3 "try-with-resources" — <https://docs.oracle.com/javase/specs/jls/se21/html/jls-14.html#jls-14.20.3>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.**

1. In §1, remove the `try`/`catch` around `wallet.pay(250)`. Predict what is printed, and whether the confirmation line appears.
2. In §2, uncomment `users.save(new Order(1002L, "mouse"))`. Predict the compiler's complaint.
3. In §2's Python version, add `users.save(Order(1002, "mouse"))` and run it. Predict what happens, then run `mypy` on it if you have it.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
