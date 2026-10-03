---
title: "Software Design Principles"
summary: "DRY, KISS and YAGNI, the three principles that keep a low-level design easy to change. DRY gives each piece of knowledge one home, but merging code that only looks alike builds the wrong abstraction; KISS picks the simplest correct design, not the shortest; YAGNI builds what is asked for now, except for decisions that are expensive to reverse. Every example runs in Java and Python, with verified output."
essential: true
---

# Software Design Principles — DRY, KISS and YAGNI

Every design decision is a guess about how the code will need to change. **DRY**, **KISS** and **YAGNI** are three rules of thumb for making good guesses. They apply at every level, from a single method to a whole system.

Each one removes a different kind of waste. DRY removes **duplicated knowledge**, so that a change only has to be made in one place. KISS removes **needless complexity**, so that the code is quick to read and hard to get wrong. YAGNI removes **speculative code**, so that you don't build and maintain features nobody asked for. Each principle also does harm if you push it too far, and this lesson shows where that point is.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- **DRY:** every piece of *knowledge* (a rule, a rate, a limit) should be defined in exactly one place. Code that only *looks* the same does not necessarily represent the same knowledge.
- **KISS:** prefer the simplest design that is *correct*, meaning the one with the fewest parts, not the fewest characters.
- **YAGNI:** build what is needed now, not what you guess will be needed later. The exception is decisions that would be expensive to undo.

</div>

This lesson covers in depth the three principles introduced in [Introduction to Low-Level Design](/synapse/low-level-design/basics/intro). Every output below was produced by running the code on Java 21 and Python 3.11.

**You'll be able to:** spot duplicated *knowledge*, not just duplicated text, and define it in one place; decide when two similar blocks of code should stay separate, using the Rule of Three and the cost of the wrong abstraction; simplify over-built code without losing correctness, including the `n % 2 == 1` trap for negative numbers; tell a speculative feature, where YAGNI applies, from a committed requirement or an expensive-to-reverse decision, where it does not.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** Each one is built in three moves:

1. **The mechanism** — what a change to the code costs, and where it has to land.
2. **A concrete bite** — a specific, runnable program where ignoring the principle (or overusing it) gives a wrong or fragile result.
3. **The earned rule** — the decision heuristic, now justified rather than asserted, plus its cost.

</div>

---

## Table of contents

1. [DRY: one fact, one place](#1-dry-one-fact-one-place)
2. [When DRY hurts](#2-when-dry-hurts)
3. [KISS: the simplest design that works](#3-kiss-the-simplest-design-that-works)
4. [YAGNI: build what is asked for now](#4-yagni-build-what-is-asked-for-now)
5. [When building ahead is right](#5-when-building-ahead-is-right)
6. [How the three pull against each other](#6-how-the-three-pull-against-each-other)
7. [Mental-model summary](#7-mental-model-summary)
8. [Gotcha checklist](#8-gotcha-checklist)
9. [Check yourself](#-check-yourself)
10. [Sources](#-sources)

---

## 1. DRY: one fact, one place

**DRY** stands for *Don't Repeat Yourself*. The original definition is about knowledge, not about text: "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system" <abbr title="Andrew Hunt and David Thomas, The Pragmatic Programmer, 1999">[1]</abbr>.

A shop shows a total in the shopping cart and again on the invoice. Both add VAT, and each has its own copy of the VAT rate. The rate has just gone up from 20% to 25%, and only the cart code was updated:

```java run
class Cart {
    static int total(int subtotal) {
        return subtotal + subtotal * 25 / 100;  // VAT raised to 25%
    }
}

class Invoice {
    static int total(int subtotal) {
        return subtotal + subtotal * 20 / 100;  // still the old 20%
    }
}

public class Main {
    public static void main(String[] args) {
        int subtotal = 100;
        System.out.println("cart total:    " + Cart.total(subtotal));
        System.out.println("invoice total: " + Invoice.total(subtotal));
    }
}
```

```python run
class Cart:
    @staticmethod
    def total(subtotal: int) -> int:
        return subtotal + subtotal * 25 // 100  # VAT raised to 25%


class Invoice:
    @staticmethod
    def total(subtotal: int) -> int:
        return subtotal + subtotal * 20 // 100  # still the old 20%


subtotal = 100
print("cart total:   ", Cart.total(subtotal))
print("invoice total:", Invoice.total(subtotal))
```

**Output:**
```
cart total:    125
invoice total: 120
```

**Analysis.** Both methods compile, run and look reasonable on their own. Together they are wrong: the customer is shown `125` but billed `120`. No compiler, and no test of a single class, catches it, because each class does exactly what its own code says. The fault is that one fact, "VAT is 25%", is stored in two places.

The fix stores the fact in one place, and both totals read it from there:

```java run
class Vat {
    static final int PERCENT = 25;

    static int addTo(int amount) {
        return amount + amount * PERCENT / 100;
    }
}

class Cart {
    static int total(int subtotal) {
        return Vat.addTo(subtotal);
    }
}

class Invoice {
    static int total(int subtotal) {
        return Vat.addTo(subtotal);
    }
}

public class Main {
    public static void main(String[] args) {
        int subtotal = 100;
        System.out.println("cart total:    " + Cart.total(subtotal));
        System.out.println("invoice total: " + Invoice.total(subtotal));
    }
}
```

```python run
class Vat:
    PERCENT = 25

    @staticmethod
    def add_to(amount: int) -> int:
        return amount + amount * Vat.PERCENT // 100


class Cart:
    @staticmethod
    def total(subtotal: int) -> int:
        return Vat.add_to(subtotal)


class Invoice:
    @staticmethod
    def total(subtotal: int) -> int:
        return Vat.add_to(subtotal)


subtotal = 100
print("cart total:   ", Cart.total(subtotal))
print("invoice total:", Invoice.total(subtotal))
```

**Output:**
```
cart total:    125
invoice total: 125
```

The next rate change needs one edit, to `Vat.PERCENT`, and both totals pick it up.

**Intuition.**
*Mechanism.* Every copy of a fact is another place that a future change must reach. With one copy, a change is one edit. With two copies, it is two edits, plus the risk that someone makes only one of them, and then nothing tells you which copy is right. The words "single, unambiguous, authoritative" in the definition name all three needs: one copy, one meaning, and one copy that everyone treats as correct.

*Concrete bite.* The first program above shows it. The duplication cost nothing on the day it was written. It cost a wrong bill on the day the rate changed, and the bug was in the class that nobody edited.

*Non-example: code that looks the same may not be the same knowledge.* Usernames and product codes were both limited to 20 characters, so someone made them share one check. Later, product codes were shortened to 8 characters, and the shared limit was changed:

```java run
class Rules {
    // Shared because usernames and product codes both allowed 20 characters.
    // Then product codes were cut to 8, and someone edited the shared value.
    static final int MAX_LENGTH = 8;

    static boolean isValid(String value) {
        return !value.isEmpty() && value.length() <= MAX_LENGTH;
    }
}

public class Main {
    public static void main(String[] args) {
        System.out.println("product code AB123456: " + Rules.isValid("AB123456"));
        System.out.println("username ada_lovelace: " + Rules.isValid("ada_lovelace"));
    }
}
```

```python run
class Rules:
    # Shared because usernames and product codes both allowed 20 characters.
    # Then product codes were cut to 8, and someone edited the shared value.
    MAX_LENGTH = 8

    @staticmethod
    def is_valid(value: str) -> bool:
        return 0 < len(value) <= Rules.MAX_LENGTH


print("product code AB123456:", Rules.is_valid("AB123456"))
print("username ada_lovelace:", Rules.is_valid("ada_lovelace"))
```

**Output** *(Java; Python prints `True` and `False`)*:
```
product code AB123456: true
username ada_lovelace: false
```

The change for product codes made a valid 12-character username fail. The two checks had the same *code*, but they expressed two different *rules*, owned by different people and free to change independently. Merging them tied together two things that were never one fact. Keep `UsernameRules.MAX_LENGTH = 20` and `ProductCode.LENGTH = 8` apart.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Before you remove duplication, ask: *if one of these changes, must the other change too?* If yes, it is one fact: define it in one place now, as a constant, a method or a class. If no, it is two facts that happen to look the same today, so keep them separate.

The cost of DRY is that shared code ties its users together: every user of the shared definition is affected when it changes. That is exactly what you want when the knowledge really is shared, and a bug when it isn't.

</div>

---

## 2. When DRY hurts

Merging two similar blocks of code creates an **abstraction**: one method or class that does the job of both. If the guess about what they have in common is wrong, the abstraction is worse than the duplication it replaced. Sandi Metz's summary is that "duplication is far cheaper than the wrong abstraction" <abbr title="Sandi Metz, The Wrong Abstraction, 2016">[2]</abbr>.

The usual protection is the **Rule of Three**, credited to Don Roberts: "The first time you do something, you just do it. The second time you do something similar, you wince at the duplication, but you do the duplicate thing anyway. The third time you do something similar, you refactor" <abbr title="Martin Fowler, Refactoring, 1999, ch. 2">[3]</abbr>. By the third copy, you can see what the copies really have in common and what differs, so the shared version is based on evidence instead of a guess.

```d2
direction: right
first: "1st time\nwrite it" { shape: rectangle }
second: "2nd time\nduplicate it, and wince" { shape: rectangle }
third: "3rd time\nextract the shared version" { shape: rectangle }
first -> second: "similar code again"
second -> third: "and again"
```

The rule is for code that *looks* the same. It is not permission to copy a business fact, such as the VAT rate, twice. A fact that you already know is shared should be defined in one place from the start.

Four situations where DRY does more harm than good:

- **Abstracting too early.** Two blocks of code look the same now, but will change for different reasons, like the username and product-code checks in §1. Merging them ties them together. *Example:* `AdminReport` and `UserReport` share `generateReport()` today, but admin reports are about to get audit columns. A shared method would soon need a flag for every difference.
- **Readability.** A shared method used by unrelated callers gradually gains flag parameters: `process(data, isOrder, skipAudit)`. Anyone reading it for one caller now has to read through code paths that don't apply to that caller. Two plain methods, `validateUser()` and `validateOrder()`, are easier to read than one with a `type` switch. When a shared method has already gone this way, Metz's advice is to copy its code back into each caller and start again <abbr title="Sandi Metz, The Wrong Abstraction, 2016">[2]</abbr>.
- **Performance-critical code, after measuring.** Calling a small helper method is usually cheap, because Java's JIT compiler can copy it into the caller. But a generic helper that wraps numbers in objects, or calls a lambda for every element, can cost real time inside a loop that runs millions of times. Keep a separate, specialised copy only when a profiler shows the cost, not on a hunch.
- **Old code without tests.** Merging duplicated logic in old, untested code can change its behaviour without anyone noticing, because the copies may differ in ways nobody remembers. First add tests that record the current behaviour, or leave the code alone until you need to change that feature anyway.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Remove duplicated *knowledge* immediately. Remove duplicated-*looking* code when it appears for the third time, once you can see what the copies really share. If a shared method starts collecting flag parameters, split it back up.

The cost of waiting is a temporary copy that you must remember to merge later. That is cheap. Untangling the wrong abstraction once many callers depend on it is not.

</div>

---

## 3. KISS: the simplest design that works

**KISS** stands for *Keep It Simple, Stupid*: out of the designs that solve the problem, prefer the one with the fewest parts. Python's design notes put it as "Simple is better than complex" and "Readability counts" <abbr title="PEP 20, The Zen of Python">[4]</abbr>.

Here are two versions of `isEven`, run on the same inputs:

```java run
class NumberUtils {
    // Too complex: an extra variable and an if-else that restate one comparison.
    static boolean isEvenVerbose(int number) {
        boolean isEven = false;
        if (number % 2 == 0) {
            isEven = true;
        } else {
            isEven = false;
        }
        return isEven;
    }

    // Simple: the comparison already is the boolean.
    static boolean isEven(int number) {
        return number % 2 == 0;
    }
}

public class Main {
    public static void main(String[] args) {
        for (int n : new int[] {4, 7, 0, -3}) {
            System.out.println(n + " " + NumberUtils.isEvenVerbose(n) + " " + NumberUtils.isEven(n));
        }
    }
}
```

```python run
class NumberUtils:
    # Too complex: an extra variable and an if-else that restate one comparison.
    @staticmethod
    def is_even_verbose(number: int) -> bool:
        is_even = False
        if number % 2 == 0:
            is_even = True
        else:
            is_even = False
        return is_even

    # Simple: the comparison already is the boolean.
    @staticmethod
    def is_even(number: int) -> bool:
        return number % 2 == 0


for n in [4, 7, 0, -3]:
    print(n, NumberUtils.is_even_verbose(n), NumberUtils.is_even(n))
```

**Output** *(Java; Python prints `True` and `False`)*:
```
4 true true
7 false false
0 true true
-3 false false
```

**Analysis.** The two columns agree for every input, including `0` and `-3`. The longer version's extra variable, its starting value of `false` and both branches added nothing, because `number % 2 == 0` is already a boolean. The extra lines only gave a reader more to check.

**Intuition.**
*Mechanism.* Every variable, branch, class and extra layer of method calls is something a reader must keep in mind, and a place where a bug can hide. Simplicity is measured by counting those parts, not characters. A design is simple when nothing more can be removed without breaking it.

*Concrete bite.* In low-level design, the usual breach of KISS is not an extra `if`. It is a design pattern used for a single case. Here, a 10% discount is wrapped in an interface, a class and a factory, next to the same rule written as one method:

```java run
// Over-built: an interface, a class and a factory for one rule.
interface DiscountPolicy {
    int apply(int amount);
}

class TenPercentOff implements DiscountPolicy {
    public int apply(int amount) {
        return amount - amount / 10;
    }
}

class DiscountPolicyFactory {
    static DiscountPolicy create(String type) {
        if (type.equals("TEN_PERCENT")) {
            return new TenPercentOff();
        }
        throw new IllegalArgumentException("unknown discount: " + type);
    }
}

// Simple: the one rule there is.
class Pricing {
    static int discounted(int amount) {
        return amount - amount / 10;
    }
}

public class Main {
    public static void main(String[] args) {
        System.out.println(DiscountPolicyFactory.create("TEN_PERCENT").apply(100));
        System.out.println(Pricing.discounted(100));
        System.out.println(DiscountPolicyFactory.create("TEN_PERCNT").apply(100));
    }
}
```

```python run
from abc import ABC, abstractmethod


# Over-built: an interface, a class and a factory for one rule.
class DiscountPolicy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...


class TenPercentOff(DiscountPolicy):
    def apply(self, amount: int) -> int:
        return amount - amount // 10


class DiscountPolicyFactory:
    @staticmethod
    def create(kind: str) -> DiscountPolicy:
        if kind == "TEN_PERCENT":
            return TenPercentOff()
        raise ValueError(f"unknown discount: {kind}")


# Simple: the one rule there is.
class Pricing:
    @staticmethod
    def discounted(amount: int) -> int:
        return amount - amount // 10


print(DiscountPolicyFactory.create("TEN_PERCENT").apply(100))
print(Pricing.discounted(100))
print(DiscountPolicyFactory.create("TEN_PERCNT").apply(100))
```

**Output** *(prints two lines, then a thrown exception; Python raises `ValueError: unknown discount: TEN_PERCNT`)*:
```
90
90
Exception in thread "main" java.lang.IllegalArgumentException: unknown discount: TEN_PERCNT
	at DiscountPolicyFactory.create(Main.java:17)
	at Main.main(Main.java:32)
```

Both designs give `90`. The pattern added three types and a string key, and the string key turned a compile-time error into a run-time error. A typo in the method name `Pricing.discounted` would not compile. The typo `TEN_PERCNT` in the string did compile, and only failed when that line ran. The interface becomes worthwhile when a second kind of discount arrives; [the design patterns chapter](/synapse/low-level-design/design-patterns/introduction-design-patterns) is about exactly those cases.

*Non-example: simple is not the same as short.* `isOdd` looks like the obvious opposite of `isEven`:

```java run
public class Main {
    static boolean isOdd(int n) {
        return n % 2 == 1;
    }

    public static void main(String[] args) {
        System.out.println("isOdd(3)  = " + isOdd(3));
        System.out.println("isOdd(-3) = " + isOdd(-3));
        System.out.println("-3 % 2    = " + (-3 % 2));
    }
}
```

```python run
def is_odd(n: int) -> bool:
    return n % 2 == 1


print("is_odd(3)  =", is_odd(3))
print("is_odd(-3) =", is_odd(-3))
print("-3 % 2     =", -3 % 2)
```

**Output (Java):**
```
isOdd(3)  = true
isOdd(-3) = false
-3 % 2    = -1
```

**Output (Python):**
```
is_odd(3)  = True
is_odd(-3) = True
-3 % 2     = 1
```

The same one-line function is correct in Python but wrong in Java. Java's `%` gives a result with the sign of the *dividend*, so `-3 % 2` is `-1` <abbr title="The Java Language Specification, Java SE 21, §15.17.3">[5]</abbr>. Python's `%` gives the sign of the *divisor*, so it is `1` <abbr title="The Python Language Reference, §6.7 Binary arithmetic operations">[6]</abbr>. Write `n % 2 != 0` instead: it is just as short, and correct in both languages. The bit trick `(n & 1) != 0` is also correct, but a reader has to understand how negative numbers are stored in binary to trust it. `% 2` says what you mean.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Write the most direct *correct* version first: a plain expression rather than a flag variable, a method rather than a class hierarchy, a class rather than a framework. Add structure only when a second, real case needs it.

The cost of KISS is that the simple version may need reworking when the second case arrives. That rework is a small change, made with real knowledge of both cases. Removing structure that all the calling code already depends on is a much bigger job.

</div>

---

## 4. YAGNI: build what is asked for now

**YAGNI** stands for *You Aren't Gonna Need It*. It comes from Extreme Programming, where Ron Jeffries put it as: "Always implement things when you actually need them, never when you just foresee that you need them" <abbr title="Ron Jeffries, You're NOT gonna need it!">[7]</abbr>.

The task is a note-taking app that lets users **create notes and view them**. The first version is written for a future that its author imagined:

```java run
import java.util.ArrayList;
import java.util.List;

// Speculative: built for categories, tags and cloud sync nobody asked for.
class Note {
    final String title;
    final String body;
    String category = "Uncategorized";        // "they'll want categories"
    final List<String> tags = new ArrayList<>(); // "and tags"
    String syncProvider = null;               // "and Google Drive sync, someday"

    Note(String title, String body) {
        this.title = title;
        this.body = body;
    }
}

class Notebook {
    private final List<Note> notes = new ArrayList<>();

    void add(Note note) { notes.add(note); }
    List<Note> all() { return notes; }

    List<Note> byCategory(String category) {
        List<Note> found = new ArrayList<>();
        for (Note n : notes) if (n.category.equals(category)) found.add(n);
        return found;
    }

    List<Note> byTag(String tag) {
        List<Note> found = new ArrayList<>();
        for (Note n : notes) if (n.tags.contains(tag)) found.add(n);
        return found;
    }

    void sync() {
        throw new UnsupportedOperationException("sync is not built yet");
    }
}

public class Main {
    public static void main(String[] args) {
        Notebook book = new Notebook();
        book.add(new Note("Groceries", "milk, eggs"));
        book.add(new Note("Ideas", "a parking-lot design"));
        for (Note n : book.all()) System.out.println(n.title + ": " + n.body);
    }
}
```

```python run
# Speculative: built for categories, tags and cloud sync nobody asked for.
class Note:
    def __init__(self, title: str, body: str):
        self.title = title
        self.body = body
        self.category = "Uncategorized"     # "they'll want categories"
        self.tags: list[str] = []           # "and tags"
        self.sync_provider = None           # "and Google Drive sync, someday"


class Notebook:
    def __init__(self):
        self._notes: list[Note] = []

    def add(self, note: Note) -> None:
        self._notes.append(note)

    def all(self) -> list[Note]:
        return self._notes

    def by_category(self, category: str) -> list[Note]:
        return [n for n in self._notes if n.category == category]

    def by_tag(self, tag: str) -> list[Note]:
        return [n for n in self._notes if tag in n.tags]

    def sync(self) -> None:
        raise NotImplementedError("sync is not built yet")


book = Notebook()
book.add(Note("Groceries", "milk, eggs"))
book.add(Note("Ideas", "a parking-lot design"))
for n in book.all():
    print(f"{n.title}: {n.body}")
```

**Output:**
```
Groceries: milk, eggs
Ideas: a parking-lot design
```

The version that does what was asked:

```java run
import java.util.ArrayList;
import java.util.List;

// What was asked for: create notes and view them.
record Note(String title, String body) {}

class Notebook {
    private final List<Note> notes = new ArrayList<>();

    void add(Note note) { notes.add(note); }
    List<Note> all() { return notes; }
}

public class Main {
    public static void main(String[] args) {
        Notebook book = new Notebook();
        book.add(new Note("Groceries", "milk, eggs"));
        book.add(new Note("Ideas", "a parking-lot design"));
        for (Note n : book.all()) System.out.println(n.title() + ": " + n.body());
    }
}
```

```python run
from dataclasses import dataclass


# What was asked for: create notes and view them.
@dataclass(frozen=True)
class Note:
    title: str
    body: str


class Notebook:
    def __init__(self):
        self._notes: list[Note] = []

    def add(self, note: Note) -> None:
        self._notes.append(note)

    def all(self) -> list[Note]:
        return self._notes


book = Notebook()
book.add(Note("Groceries", "milk, eggs"))
book.add(Note("Ideas", "a parking-lot design"))
for n in book.all():
    print(f"{n.title}: {n.body}")
```

**Output:**
```
Groceries: milk, eggs
Ideas: a parking-lot design
```

**Analysis.** The output is identical. The speculative version contains three fields and three methods that no code uses, and one of those methods throws an exception if anything ever does call it. The minimal version is short enough to read at a glance, and because `Note` can no longer be changed after it is created, it is also harder to misuse.

**Intuition.**
*Mechanism.* Martin Fowler splits the price of building a feature before it is needed into four costs <abbr title="Martin Fowler, Yagni, 2015">[8]</abbr>. The **cost of build** is the time spent writing it. The **cost of delay** is the needed work that had to wait in the meantime. The **cost of carry** is the extra complexity that everyone must work around in every later change. The **cost of repair** comes when the guess was wrong and the feature has to be reworked. Even a correct guess pays the costs of delay and carry until the feature is actually needed.

*Concrete bite.* Suppose tags *are* requested a year later, but as coloured labels shared across notebooks. The `List<String> tags` field on each note is now the wrong design. The team must convert it, and change every caller of `byTag`, before they can build what was actually asked for. The guess was right that tags would be needed, but wrong about what they would look like, which is how guesses about the future usually go wrong.

*Non-example: YAGNI is not a reason to skip tests or refactoring.* Fowler is explicit: "Yagni only applies to capabilities built into the software to support a presumptive feature, it does not apply to effort to make the software easier to modify" <abbr title="Martin Fowler, Yagni, 2015">[8]</abbr>. Tests, clear names and small classes are what make "we'll add it later" cheap. They are what makes YAGNI work, not a breach of it.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** When you hear yourself say "we might need…", stop, and build only what is needed now. Keep the code easy to change, so that adding the feature later is cheap.

The cost of YAGNI is real: sometimes you will add something later that would have been cheaper to add at the start. The trade is still worth it, because most guesses are never used, and the ones that are often turn out to need a different design.

</div>

---

## 5. When building ahead is right

YAGNI is about features built on a guess. Some work done before it is needed is not a guess:

- **The requirement has been agreed, not guessed.** *Example:* a messaging service only sends text today, but image attachments are scheduled for two sprints from now. Designing the message data model to hold attachments now avoids converting all the stored messages in two weeks' time. The test is whether someone has committed to the feature, not whether it seems likely.
- **The decision is expensive to undo.** A database schema, a public API, a file format or a network message format: once stored data or other teams depend on them, changing them means converting data and coordinating with other people. Think these through up front, even though you only build today's features on top of them.
- **Testing a known requirement early.** *Example:* a multiplayer game server must support 10,000 players at once from launch day. A load test with 10,000 simulated players in week one, while there are only 5 real testers, finds slow spots where threads block each other, before the architecture is too settled to change. That is testing a requirement you already have, not building a feature you might need.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Build ahead only for requirements that have been agreed, or for decisions that are expensive to undo. Everything else waits until someone asks for it.

Building ahead has the same four costs as any other guess. It is only worth paying them when changing later would clearly cost more, and you can explain why.

</div>

---

## 6. How the three pull against each other

The three principles usually agree. Where they disagree is where design judgement is needed:

- **DRY vs KISS.** Every abstraction that removes duplication adds a new name, and another step for the reader to follow. If the shared version is harder to read than two plain copies, KISS wins. This is the flag-parameter problem from §2.
- **DRY vs YAGNI.** A general framework built "so we never repeat ourselves" is itself a feature built on a guess. YAGNI and the Rule of Three agree: wait until the third case shows you what the shared design should really be.
- **KISS vs YAGNI.** These rarely disagree. Code built for a guessed future adds parts, so it breaks KISS too. The exceptions in §5 are the cases where a little extra complexity now makes things simpler overall.

The [SOLID principles](/synapse/low-level-design/solid-principles/solid-principles) come next. They are about *how* to structure abstractions, once you have decided they are worth building.

---

## 7. Mental-model summary

| Principle | Consequence |
|---|---|
| DRY is about knowledge, not text | Each rule, rate or limit is defined in one place, so a change is one edit |
| Copies of the same knowledge drift apart | Two copies of the VAT rate gave `125` in the cart and `120` on the invoice |
| Code that looks the same can express two different rules | Merging the username and product-code checks broke usernames when one rule changed |
| The wrong abstraction costs more than duplication | Wait for the third copy; split up a shared method that keeps gaining flags |
| KISS counts parts, not characters | Prefer a plain expression, then a method, then a class; add a pattern when a second real case appears |
| Simple must still be correct | `n % 2 == 1` fails for negative numbers in Java; `n % 2 != 0` works in Java and Python |
| YAGNI: build only what is asked for now | Speculative features pay build, delay, carry and repair costs |
| YAGNI never forbids tests or refactoring | They make adding a feature later cheap |
| Agreed requirements and hard-to-undo decisions are the exception | Plan schemas, public APIs and formats ahead; build features when they are needed |

## 8. Gotcha checklist

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

| Symptom | Likely cause | Fix |
|---|---|---|
| Two screens show different numbers after a rule changed | the same fact is stored in two places, and only one was edited | define it in one place (a constant or one method), and make both read it |
| Changing a shared helper for one caller breaks another | two different rules were merged because their code looked the same | split it back into two; merge again only if a truly shared rule appears |
| A shared method keeps gaining `boolean` flags or a `type` parameter | the abstraction doesn't fit some of its callers | copy its code back into the callers and start again |
| A one-line rule is hidden behind an interface, a class and a factory | a pattern was added before a second case existed | write the rule as a method; add the interface when a second variant arrives |
| A typo in a string key only fails at run time | the factory looks up behaviour by string instead of by type | call the method directly, or key by an `enum` once there are several cases |
| `isOdd(-3)` returns `false` in Java | Java's `%` keeps the sign of the dividend, so `-3 % 2` is `-1` | test `n % 2 != 0` |
| Fields and methods that no caller uses, or that throw "not built yet" | features built for a guessed future | delete them; add each one when it is asked for |
| "YAGNI" used as a reason to skip tests or refactoring | YAGNI applied to work that makes code easier to change | keep the tests and the refactoring; YAGNI only covers features built on a guess |

</div>

---

## ✅ Check yourself

One check per objective. Answer before you open anything.

```quiz
{"prompt": "Cart and Invoice each add VAT with their own copy of the rate. The rate changes from 20% to 25%, and only Cart is edited. For a subtotal of 100, what do the cart total and the invoice total print?", "options": ["125 and 125", "125 and 120", "120 and 120"], "answer": "125 and 120"}
```

```quiz
{"prompt": "Usernames and product codes are both limited to 20 characters today, and the length check appears in both places. What is the strongest reason to keep the two checks separate?", "options": ["They are different rules that can change independently", "Duplicated code always runs faster", "Java cannot share a constant between two classes"], "answer": "They are different rules that can change independently"}
```

```quiz
{"prompt": "In Java, isOdd is written as return n % 2 == 1;. What does isOdd(-5) return?", "options": ["true", "false", "It does not compile"], "answer": "false"}
```

```quiz
{"prompt": "Which of these is a YAGNI violation?", "options": ["Adding a syncProvider field because cloud sync might be wanted someday", "Writing tests that make the Note class safe to refactor", "Designing message storage for attachments committed for the next sprint"], "answer": "Adding a syncProvider field because cloud sync might be wanted someday"}
```

<details>
<summary>A teammate sees <code>Cart.total</code> and <code>Invoice.total</code> both calling <code>Vat.addTo</code>, and proposes a <code>PricingEngine</code> with pluggable <code>TaxStrategy</code>, <code>RoundingStrategy</code> and <code>CurrencyStrategy</code> "to keep it DRY". Which principles push back, and when would you build it?</summary>

DRY is already satisfied: the VAT rate is defined in one place, `Vat.PERCENT`, and both totals read it. The engine would not remove any duplicated knowledge.

KISS argues against it, because it adds three interfaces, and the code to connect them, to express a single rule. YAGNI argues against it, because rounding and currency strategies support features that nobody has asked for.

Build it when a second real tax rule, rounding mode or currency arrives. By then you know which parts actually vary, and the design can be based on those real cases instead of a guess.

</details>

---

## 📚 Sources

1. Andrew Hunt and David Thomas, *The Pragmatic Programmer: From Journeyman to Master* (Addison-Wesley, 1999), ch. 2, "The Evils of Duplication" — the DRY definition.
2. Sandi Metz, "The Wrong Abstraction" (20 January 2016) — <https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction>
3. Martin Fowler, *Refactoring: Improving the Design of Existing Code* (Addison-Wesley, 1999), ch. 2, "The Rule of Three" (credited to Don Roberts).
4. Tim Peters, *PEP 20 – The Zen of Python* — <https://peps.python.org/pep-0020/>
5. *The Java Language Specification, Java SE 21*, §15.17.3 "Remainder Operator `%`" — <https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.17.3>
6. *The Python Language Reference*, §6.7 "Binary arithmetic operations" (the `%` result has the sign of its second operand) — <https://docs.python.org/3/reference/expressions.html#binary-arithmetic-operations>
7. Ron Jeffries, "You're NOT gonna need it!" — <https://ronjeffries.com/xprog/articles/practices/pracnotneed/>
8. Martin Fowler, "Yagni" (26 May 2015) — <https://martinfowler.com/bliki/Yagni.html>

---

<div style="border-left:4px solid #6d28d9;background:rgba(109,40,217,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.**

1. In the §1 drift program, edit `Cart` to 30% and `Invoice` to 25%. Predict both totals, then run it.
2. Predict `isOdd(-7)` in Java and `is_odd(-7)` in Python. Then change the comparison so both print `true`.
3. Delete `byCategory`, `byTag` and `sync` from the speculative `Notebook` in §4. Predict whether the output changes, then run it.

</div>

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
