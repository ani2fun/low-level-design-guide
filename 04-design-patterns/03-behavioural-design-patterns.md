---
title: "Behavioural Design Patterns"
summary: "Iterator, Observer, and Strategy — the most common patterns for traversing collections, broadcasting events, and swapping algorithms."
essential: true
---

# Behavioural Design Patterns

Behavioral design patterns focus on how objects interact and communicate with each other, helping to define the flow of control in a system. These patterns simplify complex communication logic between objects while promoting loose coupling.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.** While structural patterns show you how to build the pipes, behavioral patterns dictate how the water flows through them. They encapsulate the moving parts of an application: state, messages, routing, and loops.

</div>

**You'll be able to:**
- Traverse collections without exposing their internal structure (Iterator).
- Notify multiple objects when state changes without tight coupling (Observer).
- Swap algorithms or logic dynamically at runtime (Strategy).

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** As you read, look for the *Mechanism* and *Concrete bite* under each code block. They map the code you just saw to the mental model you need to build.

</div>

1. [Iterator Pattern](#1-iterator-pattern)
2. [Observer Pattern](#2-observer-pattern)
3. [Strategy Pattern](#3-strategy-pattern)

## 1. Iterator Pattern

The Iterator Pattern provides a way to access the elements of a collection sequentially without exposing its underlying representation (list, array, tree, etc.).

When building a system like a playlist, exposing the internal `List` or `Array` breaks encapsulation and couples the client code to your data structure choice.

```java run
import java.util.*;

class Video {
    private String title;
    public Video(String title) { this.title = title; }
    public String getTitle() { return title; }
}

interface PlaylistIterator {
    boolean hasNext();
    Video next();
}

class YouTubePlaylistIterator implements PlaylistIterator {
    private List<Video> videos;
    private int position = 0;

    public YouTubePlaylistIterator(List<Video> videos) {
        this.videos = videos;
    }

    public boolean hasNext() { return position < videos.size(); }
    public Video next() { return hasNext() ? videos.get(position++) : null; }
}

interface Playlist {
    PlaylistIterator createIterator();
}

class YouTubePlaylist implements Playlist {
    private List<Video> videos = new ArrayList<>();
    public void addVideo(Video video) { videos.add(video); }
    public PlaylistIterator createIterator() { return new YouTubePlaylistIterator(videos); }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        YouTubePlaylist playlist = new YouTubePlaylist();
        playlist.addVideo(new Video("LLD Tutorial"));
        playlist.addVideo(new Video("System Design Basics"));

        PlaylistIterator iterator = playlist.createIterator();
        while (iterator.hasNext()) {
            System.out.println(iterator.next().getTitle());
        }
    }
}
```
```python run
from typing import List, Iterator


class Video:
    def __init__(self, title: str) -> None:
        self._title = title

    @property
    def title(self) -> str:
        return self._title


class YouTubePlaylistIterator:
    def __init__(self, videos: List[Video]) -> None:
        self._videos = videos
        self._position = 0

    def __iter__(self) -> "YouTubePlaylistIterator":
        return self

    def __next__(self) -> Video:
        if self._position >= len(self._videos):
            raise StopIteration
        video = self._videos[self._position]
        self._position += 1
        return video


class YouTubePlaylist:
    def __init__(self) -> None:
        self._videos: List[Video] = []

    def add_video(self, video: Video) -> None:
        self._videos.append(video)

    def __iter__(self) -> YouTubePlaylistIterator:
        return YouTubePlaylistIterator(self._videos)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    playlist = YouTubePlaylist()
    playlist.add_video(Video("LLD Tutorial"))
    playlist.add_video(Video("System Design Basics"))

    # `for video in playlist:` calls __iter__ then __next__ automatically.
    for video in playlist:
        print(video.title)
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `YouTubePlaylist` exposes a `createIterator()` method instead of returning its internal `List`. The client interacts only with the `PlaylistIterator` interface, meaning the playlist could swap its internal list for a database query without breaking the client. Python bakes this pattern directly into the language via the `__iter__` and `__next__` dunder methods.

**Intuition.**
- **Mechanism.** Extract the traversal behavior of a collection into a separate object (iterator).
- **Concrete bite.** A vending machine. You don't need to know how the snacks are arranged inside; you just press "Next" to scroll through options one by one.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use the Iterator pattern when you want to hide the complexity of navigating a custom data structure. The cost is the creation of additional classes (unless the language natively supports it, like Java's `Iterable` and Python's `__iter__`).

</div>

## 2. Observer Pattern

The Observer Pattern defines a one-to-many dependency between objects so that when one object (the subject) changes state, all its dependents (observers) are notified and updated automatically.

Instead of having the subject manually call distinct methods on `EmailService`, `PushNotificationService`, and `SmsService` when a video is uploaded, the subject maintains a generic list of `Subscriber`s.

```java run
import java.util.*;

interface Subscriber {
    void update(String videoTitle);
}

class EmailSubscriber implements Subscriber {
    private String email;
    public EmailSubscriber(String email) { this.email = email; }
    public void update(String videoTitle) {
        System.out.println("Email sent to " + email + ": New video - " + videoTitle);
    }
}

class MobileAppSubscriber implements Subscriber {
    private String username;
    public MobileAppSubscriber(String username) { this.username = username; }
    public void update(String videoTitle) {
        System.out.println("In-app notification for " + username + ": New video - " + videoTitle);
    }
}

interface Channel {
    void subscribe(Subscriber subscriber);
    void unsubscribe(Subscriber subscriber);
    void notifySubscribers(String videoTitle);
}

class YouTubeChannel implements Channel {
    private List<Subscriber> subscribers = new ArrayList<>();
    private String channelName;

    public YouTubeChannel(String channelName) { this.channelName = channelName; }
    public void subscribe(Subscriber subscriber) { subscribers.add(subscriber); }
    public void unsubscribe(Subscriber subscriber) { subscribers.remove(subscriber); }

    public void notifySubscribers(String videoTitle) {
        for (Subscriber subscriber : subscribers) {
            subscriber.update(videoTitle);
        }
    }

    public void uploadVideo(String videoTitle) {
        System.out.println(channelName + " uploaded: " + videoTitle);
        notifySubscribers(videoTitle);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        YouTubeChannel channel = new YouTubeChannel("techchannel");

        channel.subscribe(new MobileAppSubscriber("alex"));
        channel.subscribe(new EmailSubscriber("rahul@example.com"));

        channel.uploadVideo("Observer Pattern Explained");
    }
}
```
```python run
from abc import ABC, abstractmethod
from typing import List


class Subscriber(ABC):
    @abstractmethod
    def update(self, video_title: str) -> None: ...


class EmailSubscriber(Subscriber):
    def __init__(self, email: str) -> None:
        self._email = email

    def update(self, video_title: str) -> None:
        print(f"Email sent to {self._email}: New video - {video_title}")


class MobileAppSubscriber(Subscriber):
    def __init__(self, username: str) -> None:
        self._username = username

    def update(self, video_title: str) -> None:
        print(f"In-app notification for {self._username}: New video - {video_title}")


class YouTubeChannel:
    def __init__(self, channel_name: str) -> None:
        self._channel_name = channel_name
        self._subscribers: List[Subscriber] = []

    def subscribe(self, subscriber: Subscriber) -> None:
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber: Subscriber) -> None:
        self._subscribers.remove(subscriber)

    def notify_subscribers(self, video_title: str) -> None:
        for subscriber in self._subscribers:
            subscriber.update(video_title)

    def upload_video(self, video_title: str) -> None:
        print(f"{self._channel_name} uploaded: {video_title}")
        self.notify_subscribers(video_title)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    channel = YouTubeChannel("techchannel")

    channel.subscribe(MobileAppSubscriber("alex"))
    channel.subscribe(EmailSubscriber("rahul@example.com"))

    channel.upload_video("Observer Pattern Explained")
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `YouTubeChannel` does not know if its subscribers are emails, push notifications, or SMS clients. It only knows they implement `Subscriber`. This loose coupling makes it trivial to add a new notification mechanism without touching the core `YouTubeChannel` code.

**Intuition.**
- **Mechanism.** Maintain a list of listener interfaces, and loop through them to trigger an update method when state changes.
- **Concrete bite.** Subscribing to a newsletter. The publisher doesn't know who you are; they just add your address to a list and blast an email to everyone on the list when a new issue drops.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use the Observer pattern when changes to one object require changing others, and you don't know how many objects need to be changed beforehand. The cost is that subscribers are notified in an arbitrary order, and forgetting to unsubscribe can cause memory leaks.

</div>

## 3. Strategy Pattern

The Strategy Pattern lets you define a family of algorithms, put each of them into a separate class, and make their objects interchangeable at runtime.

Instead of a giant `if-else` or `switch` block calculating shipping costs based on the provider (FedEx, UPS, USPS), you extract each calculation into its own strategy class.

```java run
interface PaymentStrategy {
    void pay(double amount);
}

class CreditCardPayment implements PaymentStrategy {
    private String cardNumber;
    public CreditCardPayment(String cardNumber) { this.cardNumber = cardNumber; }
    public void pay(double amount) { System.out.println("Paid ₹" + amount + " using Credit Card."); }
}

class UPIPayment implements PaymentStrategy {
    private String upiId;
    public UPIPayment(String upiId) { this.upiId = upiId; }
    public void pay(double amount) { System.out.println("Paid ₹" + amount + " using UPI."); }
}

class CheckoutCart {
    private PaymentStrategy paymentStrategy;

    // The strategy can be changed dynamically
    public void setPaymentStrategy(PaymentStrategy paymentStrategy) {
        this.paymentStrategy = paymentStrategy;
    }

    public void checkout(double amount) {
        if (paymentStrategy == null) {
            System.out.println("Please select a payment method.");
            return;
        }
        paymentStrategy.pay(amount);
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        CheckoutCart cart = new CheckoutCart();

        cart.setPaymentStrategy(new CreditCardPayment("1234-5678-9012"));
        cart.checkout(1500.0);

        cart.setPaymentStrategy(new UPIPayment("user@upi"));
        cart.checkout(500.0);
    }
}
```
```python run
from abc import ABC, abstractmethod


class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> None: ...


class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number: str) -> None:
        self._card_number = card_number

    def pay(self, amount: float) -> None:
        print(f"Paid ₹{amount} using Credit Card.")


class UPIPayment(PaymentStrategy):
    def __init__(self, upi_id: str) -> None:
        self._upi_id = upi_id

    def pay(self, amount: float) -> None:
        print(f"Paid ₹{amount} using UPI.")


class CheckoutCart:
    def __init__(self) -> None:
        self._payment_strategy: PaymentStrategy | None = None

    def set_payment_strategy(self, strategy: PaymentStrategy) -> None:
        self._payment_strategy = strategy

    def checkout(self, amount: float) -> None:
        if not self._payment_strategy:
            print("Please select a payment method.")
            return
        self._payment_strategy.pay(amount)


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    cart = CheckoutCart()

    cart.set_payment_strategy(CreditCardPayment("1234-5678-9012"))
    cart.checkout(1500.0)

    cart.set_payment_strategy(UPIPayment("user@upi"))
    cart.checkout(500.0)
```

**Output:**
```text
@@OUT@@
```

**Analysis.** The `CheckoutCart` context doesn't know how the payment is processed. It delegates the `pay()` action to the currently attached `PaymentStrategy`. This adheres to the Open/Closed Principle: adding a `CryptoPayment` strategy requires zero changes to the `CheckoutCart`.

**Intuition.**
- **Mechanism.** Extract differing algorithms into separate classes implementing the same interface, and inject the required one into a context object.
- **Concrete bite.** Google Maps routing. The context is "Get Directions". You can swap the strategy from "Driving" to "Walking" to "Transit", and the map recalculates without changing the core mapping UI.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use Strategy to replace giant conditionals that switch on variants of an algorithm. The cost is an increase in the number of classes in the system.

</div>

## Summary

| Pattern | Purpose |
|---|---|
| **Iterator** | Extracts the traversal of a collection into a separate object, hiding the underlying data structure. |
| **Observer** | Lets objects subscribe to events and receive automatic notifications when state changes. |
| **Strategy** | Extracts interchangeable algorithms into separate classes, allowing them to be swapped at runtime. |

## 🚨 Gotcha Checklist
| Symptom | Likely cause | Fix |
|---|---|---|
| A UI button click crashes because the listener tries to update a component that no longer exists. | **Dangling Observer.** The observer was destroyed but never unsubscribed from the subject. | Always call `unsubscribe()` when an observer is garbage collected or disposed. |
| You have 15 different strategy classes, but they only differ by one tiny constant multiplier. | **Over-engineering Strategy.** You are turning simple data variations into entire classes. | Use Strategy for differing *behavior/logic*, not just differing configuration data. |

## ✅ Check yourself

```quiz
{
  "prompt": "If you are building a mapping application that needs to calculate routes for walking, driving, and public transit, which pattern helps you swap the routing algorithm dynamically?",
  "options": [
    "Strategy",
    "Observer",
    "Iterator",
    "Adapter"
  ],
  "answer": "Strategy"
}
```

```quiz
{
  "prompt": "Which pattern is built directly into Java via the `Iterable` interface and Python via the `__iter__` method?",
  "options": [
    "Iterator",
    "Observer",
    "Strategy",
    "Command"
  ],
  "answer": "Iterator"
}
```

<details>
<summary>How is Strategy different from State? They both swap behavior dynamically.</summary>

In the **Strategy** pattern, the client explicitly chooses and injects the strategy (e.g., the user clicks "Pay with Credit Card"). In the **State** pattern, the context changes its own state internally based on events (e.g., a vending machine moves from `IdleState` to `HasCoinState` on its own).
</details>

## 📚 Sources
- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.

<div style="border-left:4px solid #8e155c;background:rgba(142,21,92,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** 
If a `YouTubeChannel` has 10,000 subscribers, what happens when it calls `notifySubscribers()`?

It will block the thread while iterating over the list and calling `update()` 10,000 times synchronously. For high-scale systems, the pure Observer pattern is usually replaced by asynchronous message brokers (like Kafka) to decouple the execution time.

</div>

## Your Turn

Find a giant `if-else` block or `switch` statement in your codebase that chooses how to process a file, format an output, or handle a request. Extract each branch into a Strategy class, and inject the chosen strategy instead.
