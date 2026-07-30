---
title: "Introduction to Design Patterns"
summary: "What design patterns are, where they came from, and the three GoF categories that organize them."
essential: true
---

# Introduction to Design Patterns

Design patterns are a foundational concept in software engineering, especially when building scalable and maintainable systems. In this article, we explore what design patterns are, why they matter, how they originated, and how they are categorized. This introduction sets the stage for deeper dives into individual patterns in upcoming discussions.

## What Are Design Patterns?

Design patterns are standard, time-tested solutions to common software design problems. They are not code templates but abstract descriptions or blueprints that help developers solve issues in code architecture and system design.

To put it simply: Design patterns help you avoid reinventing the wheel when facing recurring design challenges.

### Real-World Analogy

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** Think of design patterns like recipes in cooking. If you want to bake a cake, you don't experiment from scratch each time - you follow a proven recipe. Similarly, design patterns are tried-and-tested “recipes” for solving common coding problems efficiently and consistently.

</div>

## The Origin of Design Patterns

The idea of design patterns was formalized by the Gang of Four (GoF) - Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides - in their seminal 1994 book "Design Patterns: Elements of Reusable Object-Oriented Software."

They cataloged 23 design patterns that were repeatedly seen in object-oriented software development and grouped them into three major categories.

## The Three Categories of Design Patterns

```mermaid
flowchart TD
    GoF["Design Patterns<br/>(Gang of Four — 23 patterns)"]
    GoF --> C["Creational<br/><i>object creation</i>"]
    GoF --> S["Structural<br/><i>object composition</i>"]
    GoF --> B["Behavioral<br/><i>object interaction</i>"]
    C --> Cx["Singleton · Factory Method<br/>Abstract Factory · Builder · Prototype"]
    S --> Sx["Adapter · Bridge · Composite · Decorator<br/>Facade · Flyweight · Proxy"]
    B --> Bx["Observer · Strategy · Command · State · Iterator<br/>Mediator · Chain of Responsibility · Template Method<br/>Visitor · Memento · Interpreter"]
    classDef root fill:#f3f4f6,stroke:#6b7280,color:#111827;
    classDef creational fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef structural fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef behavioral fill:#f3e8ff,stroke:#9333ea,color:#581c87;
    class GoF root;
    class C,Cx creational;
    class S,Sx structural;
    class B,Bx behavioral;
```

### 1. Creational Patterns

These focus on object creation mechanisms, trying to create objects in a manner suitable to the situation. They abstract the instantiation process, making the system independent of how its objects are created.

### Real-World Analogy

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** Imagine ordering a drink at a vending machine. You press a button (say “Orange Juice”), and the machine internally figures out how to prepare it - whether to pour from a bottle, mix a concentrate, or use a fresh dispenser. You don't care how it's made - you just get your drink.

</div>

This is similar to the Factory Pattern, where the creation logic is hidden from the user and abstracted for flexibility.

Examples include:

- Singleton Pattern
- Factory Method
- Abstract Factory Pattern
- Builder Pattern
- Prototype Pattern

### 2. Structural Patterns

These deal with object composition - how classes and objects can be combined to form larger structures while keeping the system flexible and efficient. It helps systems to work together that otherwise could not because of incompatible interfaces.

### Real-World Analogy

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** Suppose you have a modern smartphone (your system) that uses a USB-C charger, but your old power adapter only supports micro-USB. Instead of replacing either device, you use an adapter that connects the two.

</div>

That adapter is like a structural pattern (specifically, the Adapter Pattern) - it allows incompatible components to work together seamlessly without changing their internals.

Examples include:

- Adapter Pattern
- Bridge Pattern
- Composite Pattern
- Decorator Pattern
- Facade Pattern
- Flyweight Pattern
- Proxy Pattern

### 3. Behavioral Patterns

These are concerned with object interaction and responsibility - how they communicate and assign responsibilities while ensuring loose coupling.

### Real-World Analogy

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** Think of a restaurant. The waiter takes your order and passes it to the kitchen. You don't talk directly to the chef - the waiter acts as a mediator between you and the kitchen.

</div>

This reflects the Mediator Pattern, which defines an object that controls communication between other objects, preventing tight interdependencies.

Examples include:

- Observer Pattern
- Strategy Pattern
- Interpreter Pattern
- Command Pattern
- Chain of Responsibility
- Mediator Pattern
- State Pattern
- Template Method
- Visitor Pattern
- Iterator Pattern
- Memento Pattern

This is just a brief overview of design patterns. Each pattern has its own unique characteristics, advantages, and use cases. In the following topics, we will delve deeper into each category and explore specific patterns in detail.
</content>
