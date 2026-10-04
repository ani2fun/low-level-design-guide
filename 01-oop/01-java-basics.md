---
title: "Java Basics"
summary: "What Java this book assumes, and where to learn it. The Java guide is the single source of truth for the language: syntax, control flow, classes, collections, exceptions and generics. This page maps each topic to its Java guide lesson and lists what you should be able to read before the design chapters."
essential: true
---

# Java Basics — What This Book Assumes, and Where to Learn It

This book teaches **design**: how to split a system into classes, give each class a clear job, and connect them so that the system is easy to change. Its examples are written in Java, with Python versions alongside. It does not teach the Java language itself.

The Java language is taught in one place, the **[Java guide](/synapse/programming-languages/java/first-steps/what-java-is-and-running-code)**. Every Java rule this book relies on is explained there, once, with verified output, so the two books never disagree. This page tells you which parts of the Java guide you need, and in what order.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.**

- **The Java guide teaches the language; this book uses it.** When a lesson here needs a Java rule, it links to the Java guide instead of repeating it.
- To follow the design chapters, you need the Java guide's first three chapters, plus its lessons on collections, exceptions and interfaces.
- The rest of this chapter covers what the language lessons don't: how to use the OOP ideas as *design* tools.

</div>

---

## Table of contents

1. [What you need before the design chapters](#1-what-you-need-before-the-design-chapters)
2. [Where each topic lives in the Java guide](#2-where-each-topic-lives-in-the-java-guide)
3. [How this chapter continues](#3-how-this-chapter-continues)
4. [Check yourself](#-check-yourself)

---

## 1. What you need before the design chapters

You are ready for the rest of this book if you can read the code below and predict what it prints. It uses a class, a constructor, a private field, a method, a list and a loop, which covers most of what the design examples need.

```java run
import java.util.ArrayList;
import java.util.List;

class Cart {
    private final List<Integer> pricesInCents = new ArrayList<>();

    void add(int cents) {
        pricesInCents.add(cents);
    }

    int total() {
        int sum = 0;
        for (int p : pricesInCents) sum += p;
        return sum;
    }
}

public class Main {
    public static void main(String[] args) {
        Cart cart = new Cart();
        cart.add(1999);
        cart.add(500);
        System.out.println("items total: " + cart.total() + " cents");
    }
}
```

```python run
class Cart:
    def __init__(self) -> None:
        self._prices_in_cents: list[int] = []

    def add(self, cents: int) -> None:
        self._prices_in_cents.append(cents)

    def total(self) -> int:
        return sum(self._prices_in_cents)


cart = Cart()
cart.add(1999)
cart.add(500)
print(f"items total: {cart.total()} cents")
```

**Output:**
```
items total: 2499 cents
```

If any line of the Java version is unclear, the lessons in section 2 cover it.

---

## 2. Where each topic lives in the Java guide

**Start here** (needed for every chapter):

| Topic | Java guide lesson |
|---|---|
| What Java is, compiling and running a program | [What Java Is & Running Code](/synapse/programming-languages/java/first-steps/what-java-is-and-running-code) |
| Variables, primitive types, type casting | [Variables & Primitive Types](/synapse/programming-languages/java/first-steps/variables-and-primitive-types) |
| Operators and arithmetic | [Numbers & Arithmetic](/synapse/programming-languages/java/first-steps/numbers-and-arithmetic) |
| Strings | [Strings, the Basics](/synapse/programming-languages/java/first-steps/strings-the-basics) |
| Reading input, printing output | [Input & Output](/synapse/programming-languages/java/first-steps/input-and-output) |
| Booleans, `if`/`switch`, loops | [Booleans & Logic](/synapse/programming-languages/java/control-flow/booleans-and-logic), [Conditionals](/synapse/programming-languages/java/control-flow/conditionals), [Loops](/synapse/programming-languages/java/control-flow/loops) |
| Arrays | [Arrays](/synapse/programming-languages/java/control-flow/arrays) |
| Methods, parameters, return values | [Methods](/synapse/programming-languages/java/control-flow/methods) |
| Classes, objects, fields, constructors | [Defining Classes & Creating Objects](/synapse/programming-languages/java/classes-and-objects/classes-and-objects) |
| `private`, `public`, getters and setters | [Encapsulation & Access Modifiers](/synapse/programming-languages/java/classes-and-objects/encapsulation-and-access-modifiers) |
| `static` members | [static vs Instance](/synapse/programming-languages/java/classes-and-objects/static-vs-instance) |
| References, `==` vs `equals`, `null` | [References, Equality & the Object Model](/synapse/programming-languages/java/classes-and-objects/references-equality-and-the-object-model) |

**Needed by the OOP, SOLID and design-pattern chapters:**

| Topic | Java guide lesson |
|---|---|
| Lists, maps, sets | [The Collections Framework](/synapse/programming-languages/java/core-libraries/the-collections-framework), [Sets & Maps](/synapse/programming-languages/java/core-libraries/sets-and-maps) |
| `equals` and `hashCode` for objects in collections | [equals & hashCode](/synapse/programming-languages/java/core-libraries/equals-and-hashcode) |
| Generics | [Generics](/synapse/programming-languages/java/core-libraries/generics) |
| Enums and records | [Enums & Records](/synapse/programming-languages/java/core-libraries/enums-and-records) |
| Inheritance, overriding, `super`, polymorphism | [Inheritance & Polymorphism](/synapse/programming-languages/java/robust-oop/inheritance-and-polymorphism) |
| Abstract classes and interfaces | [Abstract Classes & Interfaces](/synapse/programming-languages/java/robust-oop/abstract-classes-and-interfaces) |
| Exceptions: `try`/`catch`/`finally`, checked vs unchecked, custom exceptions | [Exceptions](/synapse/programming-languages/java/robust-oop/exceptions) |
| Nested and anonymous classes, lambdas | [Nested & Anonymous Classes; Lambdas](/synapse/programming-languages/java/robust-oop/nested-and-anonymous-classes-and-lambdas) |

**Needed by the concurrency chapter:** [Concurrency: the Basics](/synapse/programming-languages/java/advanced/concurrency-the-basics), [Concurrency: Coordination](/synapse/programming-languages/java/advanced/concurrency-coordination) and [Concurrency: High-Level & Virtual Threads](/synapse/programming-languages/java/advanced/concurrency-high-level-and-virtual-threads).

**Python.** Most examples in this book also have a Python version, placed next to the Java one. The Python versions use only the standard library and are written to be read without a separate Python course.

---

## 3. How this chapter continues

The next lessons use the object-oriented ideas as design tools, and link back to the Java guide for the language rules:

1. [Encapsulation, Inheritance & Polymorphism](/synapse/low-level-design/oop/encapsulation-access-modifiers-inheritance-polymorphism): protecting invariants, when inheritance is the wrong tool, and replacing type checks with polymorphism.
2. [Abstraction & Interfaces](/synapse/low-level-design/oop/abstraction-interfaces-static-members-inner-classes): programming to a contract, interface or abstract class, and the design cost of `static`.
3. [Errors, Generics & Resources in Design](/synapse/low-level-design/oop/exception-generics-file-handling-obj-lifecycle): exceptions as part of an API, generic components, and who owns a resource.
4. [Relationships and Object Behaviour](/synapse/low-level-design/oop/relationships-and-object-behaviour): association, aggregation and composition, and copying objects.

---

## ✅ Check yourself

Answer these before moving on. If one is hard, follow its link in section 2.

```quiz
{"prompt": "In the Cart class above, can code outside Cart call cart.pricesInCents.clear()?", "options": ["No: the field is private", "Yes: every field is visible inside the same file", "Only if Cart is public"], "answer": "No: the field is private"}
```

```quiz
{"prompt": "What does new Cart() do?", "options": ["Creates a Cart object and runs its constructor", "Declares a new class called Cart", "Copies an existing Cart"], "answer": "Creates a Cart object and runs its constructor"}
```

```quiz
{"prompt": "Two String variables a and b hold equal text that was built separately. Which comparison is reliably true?", "options": ["a.equals(b)", "a == b", "Both"], "answer": "a.equals(b)"}
```

## Your Turn

Before you move on, check your understanding with the coach — explain the idea, apply it, weigh the trade-offs, then defend your reasoning.

<div class="concept-coach"></div>
