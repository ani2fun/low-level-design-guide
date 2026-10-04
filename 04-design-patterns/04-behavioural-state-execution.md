---
title: "State & Execution Patterns"
summary: "Command, Template Method, and State — behavioral patterns for encapsulating actions, standardizing workflows, and managing state transitions."
essential: true
---

# State & Execution Patterns

While some behavioral patterns focus on routing messages (like Observer), others focus on how an action is encapsulated, scheduled, or executed over time.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.** You can turn an action or a state into a standalone object. This lets you pass actions around as variables, queue them, undo them, or allow an object to completely change its behavior as its internal state changes.

</div>

**You'll be able to:**
- Encapsulate a request as an object to support queues and undo operations (Command).
- Define the skeleton of an algorithm while letting subclasses fill in the steps (Template Method).
- Allow an object to alter its behavior when its internal state changes (State).

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** As you read, look for the *Mechanism* and *Concrete bite* under each code block. They map the code you just saw to the mental model you need to build.

</div>

1. [Command Pattern](#1-command-pattern)
2. [Template Method Pattern](#2-template-method-pattern)
3. [State Pattern](#3-state-pattern)

## 1. Command Pattern

The Command Pattern encapsulates a request as an object. This lets you parameterize methods with different requests, delay or queue a request's execution, and support undoable operations.

Instead of a UI button directly calling `light.turnOn()`, the button calls `execute()` on a `Command` object that it holds.

```java run
import java.util.*;

// Receiver: the object performing the actual work
class Light {
    public void turnOn() { System.out.println("Light is ON"); }
    public void turnOff() { System.out.println("Light is OFF"); }
}

interface Command {
    void execute();
    void undo();
}

class LightOnCommand implements Command {
    private Light light;
    public LightOnCommand(Light light) { this.light = light; }
    public void execute() { light.turnOn(); }
    public void undo() { light.turnOff(); }
}

class LightOffCommand implements Command {
    private Light light;
    public LightOffCommand(Light light) { this.light = light; }
    public void execute() { light.turnOff(); }
    public void undo() { light.turnOn(); }
}

// Invoker: the object that triggers the command
class RemoteControl {
    private Command command;
    private Stack<Command> history = new Stack<>();

    public void setCommand(Command command) { this.command = command; }
    
    public void pressButton() {
        command.execute();
        history.push(command);
    }
    
    public void pressUndo() {
        if (!history.isEmpty()) {
            history.pop().undo();
        }
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Light livingRoomLight = new Light();
        Command lightOn = new LightOnCommand(livingRoomLight);
        Command lightOff = new LightOffCommand(livingRoomLight);

        RemoteControl remote = new RemoteControl();

        remote.setCommand(lightOn);
        remote.pressButton();

        remote.setCommand(lightOff);
        remote.pressButton();

        System.out.println("-- Undoing --");
        remote.pressUndo();
        remote.pressUndo();
    }
}
```
```python run
from abc import ABC, abstractmethod
from typing import List


class Light:
    def turn_on(self) -> None: print("Light is ON")
    def turn_off(self) -> None: print("Light is OFF")


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...


class LightOnCommand(Command):
    def __init__(self, light: Light) -> None:
        self._light = light
    def execute(self) -> None: self._light.turn_on()
    def undo(self) -> None: self._light.turn_off()


class LightOffCommand(Command):
    def __init__(self, light: Light) -> None:
        self._light = light
    def execute(self) -> None: self._light.turn_off()
    def undo(self) -> None: self._light.turn_on()


class RemoteControl:
    def __init__(self) -> None:
        self._command: Command | None = None
        self._history: List[Command] = []

    def set_command(self, command: Command) -> None:
        self._command = command

    def press_button(self) -> None:
        if self._command:
            self._command.execute()
            self._history.append(self._command)

    def press_undo(self) -> None:
        if self._history:
            self._history.pop().undo()


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    living_room_light = Light()
    light_on = LightOnCommand(living_room_light)
    light_off = LightOffCommand(living_room_light)

    remote = RemoteControl()

    remote.set_command(light_on)
    remote.press_button()

    remote.set_command(light_off)
    remote.press_button()

    print("-- Undoing --")
    remote.press_undo()
    remote.press_undo()
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `RemoteControl` is completely decoupled from the `Light`. Because the action is encapsulated in a `Command` object, the remote can store a history of executed commands and support `undo()` by popping the stack.

**Intuition.**
- **Mechanism.** Wrap a request inside an object that has an `execute()` method. Pass this object to the invoker.
- **Concrete bite.** Ordering food at a restaurant. You tell the waiter what you want (the Command). The waiter writes it on a ticket and puts it on the kitchen queue. The chef (the Receiver) eventually cooks it.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use Command when you need to queue operations, schedule their execution, or support undo/redo. The cost is a slew of small classes for every possible action.

</div>

## 2. Template Method Pattern

The Template Method Pattern defines the skeleton of an algorithm in a superclass, but lets subclasses override specific steps of the algorithm without changing its overall structure.

```java run
abstract class BeverageMaker {
    // The Template Method: marked final so subclasses can't change the sequence
    public final void makeBeverage() {
        boilWater();
        brew();
        pourInCup();
        addCondiments();
    }

    private void boilWater() { System.out.println("Boiling water"); }
    private void pourInCup() { System.out.println("Pouring into cup"); }

    // Steps to be implemented by subclasses
    protected abstract void brew();
    protected abstract void addCondiments();
}

class TeaMaker extends BeverageMaker {
    protected void brew() { System.out.println("Steeping the tea"); }
    protected void addCondiments() { System.out.println("Adding lemon"); }
}

class CoffeeMaker extends BeverageMaker {
    protected void brew() { System.out.println("Dripping coffee through filter"); }
    protected void addCondiments() { System.out.println("Adding sugar and milk"); }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        System.out.println("Making tea:");
        BeverageMaker tea = new TeaMaker();
        tea.makeBeverage();

        System.out.println("\nMaking coffee:");
        BeverageMaker coffee = new CoffeeMaker();
        coffee.makeBeverage();
    }
}
```
```python run
from abc import ABC, abstractmethod


class BeverageMaker(ABC):
    # Python has no 'final' keyword enforcement, but by convention,
    # the template method is left un-overridden by subclasses.
    def make_beverage(self) -> None:
        self._boil_water()
        self._brew()
        self._pour_in_cup()
        self._add_condiments()

    def _boil_water(self) -> None: print("Boiling water")
    def _pour_in_cup(self) -> None: print("Pouring into cup")

    @abstractmethod
    def _brew(self) -> None: ...
    @abstractmethod
    def _add_condiments(self) -> None: ...


class TeaMaker(BeverageMaker):
    def _brew(self) -> None: print("Steeping the tea")
    def _add_condiments(self) -> None: print("Adding lemon")


class CoffeeMaker(BeverageMaker):
    def _brew(self) -> None: print("Dripping coffee through filter")
    def _add_condiments(self) -> None: print("Adding sugar and milk")


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    print("Making tea:")
    tea = TeaMaker()
    tea.make_beverage()

    print("\nMaking coffee:")
    coffee = CoffeeMaker()
    coffee.make_beverage()
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `makeBeverage()` method defines the unchangeable workflow. `TeaMaker` and `CoffeeMaker` only provide the implementation for the varying steps (`brew()` and `addCondiments()`). This prevents code duplication for the shared steps (`boilWater()` and `pourInCup()`).

**Intuition.**
- **Mechanism.** Create an abstract base class with a final "template method" that calls abstract placeholder methods. Subclasses implement the placeholders.
- **Concrete bite.** Building a mass-production house. The architect defines the exact sequence (foundation, walls, roof), but the buyer can choose what goes inside the walls (brick vs. siding).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use Template Method when multiple classes share the exact same algorithm structure but differ in specific steps. The cost is rigid reliance on inheritance.

</div>

## 3. State Pattern

The State Pattern allows an object to alter its behavior when its internal state changes. The object will appear to change its class.

Instead of a giant `if (state == PLAYING) ... else if (state == PAUSED)` block inside a media player, you represent each state as an object, and the player delegates actions to its current state object.

```java run
interface VendingMachineState {
    void insertCoin();
    void dispenseItem();
}

class VendingMachine {
    private VendingMachineState idleState;
    private VendingMachineState hasCoinState;
    private VendingMachineState currentState;

    public VendingMachine() {
        idleState = new IdleState(this);
        hasCoinState = new HasCoinState(this);
        currentState = idleState; // initial state
    }

    public void setState(VendingMachineState state) { this.currentState = state; }
    public VendingMachineState getIdleState() { return idleState; }
    public VendingMachineState getHasCoinState() { return hasCoinState; }

    public void insertCoin() { currentState.insertCoin(); }
    public void dispenseItem() { currentState.dispenseItem(); }
}

class IdleState implements VendingMachineState {
    private VendingMachine machine;
    public IdleState(VendingMachine machine) { this.machine = machine; }

    public void insertCoin() {
        System.out.println("Coin accepted. You can now dispense.");
        machine.setState(machine.getHasCoinState());
    }
    public void dispenseItem() {
        System.out.println("Insert a coin first.");
    }
}

class HasCoinState implements VendingMachineState {
    private VendingMachine machine;
    public HasCoinState(VendingMachine machine) { this.machine = machine; }

    public void insertCoin() {
        System.out.println("Coin already inserted.");
    }
    public void dispenseItem() {
        System.out.println("Item dispensed.");
        machine.setState(machine.getIdleState());
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        VendingMachine machine = new VendingMachine();
        
        machine.dispenseItem(); // Fails, in IdleState
        machine.insertCoin();   // Transitions to HasCoinState
        machine.insertCoin();   // Fails, already has coin
        machine.dispenseItem(); // Succeeds, transitions to IdleState
    }
}
```
```python run
from __future__ import annotations
from abc import ABC, abstractmethod


class VendingMachineState(ABC):
    @abstractmethod
    def insert_coin(self) -> None: ...
    @abstractmethod
    def dispense_item(self) -> None: ...


class VendingMachine:
    def __init__(self) -> None:
        self.idle_state = IdleState(self)
        self.has_coin_state = HasCoinState(self)
        self._current_state: VendingMachineState = self.idle_state

    def set_state(self, state: VendingMachineState) -> None:
        self._current_state = state

    def insert_coin(self) -> None:
        self._current_state.insert_coin()

    def dispense_item(self) -> None:
        self._current_state.dispense_item()


class IdleState(VendingMachineState):
    def __init__(self, machine: VendingMachine) -> None:
        self._machine = machine

    def insert_coin(self) -> None:
        print("Coin accepted. You can now dispense.")
        self._machine.set_state(self._machine.has_coin_state)

    def dispense_item(self) -> None:
        print("Insert a coin first.")


class HasCoinState(VendingMachineState):
    def __init__(self, machine: VendingMachine) -> None:
        self._machine = machine

    def insert_coin(self) -> None:
        print("Coin already inserted.")

    def dispense_item(self) -> None:
        print("Item dispensed.")
        self._machine.set_state(self._machine.idle_state)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    machine = VendingMachine()

    machine.dispense_item()
    machine.insert_coin()
    machine.insert_coin()
    machine.dispense_item()
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `VendingMachine` delegates `insertCoin()` and `dispenseItem()` to `currentState`. By swapping the `currentState` variable from `IdleState` to `HasCoinState`, the machine completely changes how it responds to the exact same method calls.

**Intuition.**
- **Mechanism.** Represent states as classes. The context delegates execution to its current state object. The state objects can trigger transitions by passing a new state to the context.
- **Concrete bite.** Your smartphone's power button. If the phone is locked, it wakes the screen. If the phone is unlocked, it locks it. The button does the same thing, but the phone's internal state dictates the result.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use the State pattern when an object behaves wildly differently depending on its current state, and you have massive conditional blocks managing these transitions. The cost is that state transition logic can become scattered across multiple state classes.

</div>

## Summary

| Pattern | Purpose |
|---|---|
| **Command** | Encapsulates a request as an object, allowing for queues, logging, and undo operations. |
| **Template Method** | Defines an algorithm's skeleton in a base class, letting subclasses override specific steps. |
| **State** | Lets an object alter its behavior when its internal state changes by delegating to a state object. |

## 🚨 Gotcha Checklist
| Symptom | Likely cause | Fix |
|---|---|---|
| The history stack in your Command pattern is consuming too much RAM. | **Heavy Commands.** Your command objects are storing large amounts of state (like an entire file backup) for undo. | Store only the *delta* (what changed) or use the Memento pattern to serialize state compactly. |
| You want to use Template Method, but Java doesn't support multiple inheritance, so you can't inherit the template. | **Inheritance restriction.** Template Method relies heavily on inheritance. | Switch to the Strategy pattern, which uses composition instead. |

## ✅ Check yourself

```quiz
{
  "prompt": "Which pattern is the foundation for implementing 'Undo' and 'Redo' functionality in text editors?",
  "options": [
    "Command",
    "State",
    "Template Method",
    "Strategy"
  ],
  "answer": "Command"
}
```

```quiz
{
  "prompt": "If you find yourself writing `if (status == DRAFT) ... else if (status == PUBLISHED) ...` inside every single method of an article class, which pattern cleans this up?",
  "options": [
    "State",
    "Template Method",
    "Command",
    "Observer"
  ],
  "answer": "State"
}
```

<details>
<summary>How does the State pattern differ from Strategy? Structurally, they look identical.</summary>

They are structurally identical (Context -> Interface -> Concrete Implementations), but differ in intent. In **Strategy**, the client injects the strategy, and the strategies don't know about each other. In **State**, the state objects typically hold a reference to the context and trigger transitions to other states themselves.
</details>

## 📚 Sources
- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.

<div style="border-left:4px solid #8e155c;background:rgba(142,21,92,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** 
In the Template Method pattern, can a subclass override the main template method?

If written correctly, no. In Java, the template method should be marked `final` so subclasses cannot break the sequence of the algorithm. They can only override the protected abstract steps.

</div>

## Your Turn

Think of an algorithm in your codebase that involves fetching data, transforming it, and saving it. Create an abstract `DataPipeline` class with a `final void execute()` method that dictates this flow. Subclass it into `XmlToDatabasePipeline` and `JsonToFilePipeline`.
