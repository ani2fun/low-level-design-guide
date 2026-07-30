---
title: "Relationships and Object Behaviour"
summary: "How classes connect through association, aggregation, and composition, and how objects are duplicated through shallow and deep cloning — with worked Java examples and practice problems."
essential: true
---

# Relationships and Object Behaviour

In object-oriented programming (OOP), classes are the foundational building blocks that define the structure and behavior of objects. One of the most important concepts in OOP is how these classes interact with each other.

These interactions, or relationships, allow developers to model real-world systems effectively. This article delves into the key types of relationships between classes: association, aggregation, and composition.

Relationships between classes can be categorized into three major types:

- **Association**: A general relationship where one class interacts with another.
- **Aggregation**: A specialized form of association that represents a "has-a" relationship with a weaker bond.
- **Composition**: A more restrictive form of aggregation where the lifecycle of the related objects is tightly coupled.

## Association

Association defines how two classes are connected.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** It represents a situation where objects of one class interact with objects of another through some form of linkage or reference.

</div>

This interaction can manifest in various ways, depending on the context of the relationship.

The connection can be one-to-one, one-to-many, or many-to-many, enabling different levels of collaboration and data sharing between the classes. Understanding this fundamental concept is key to designing systems that mirror real-world interactions.

### Types of Association

- **One-to-One**: One instance of a class is associated with exactly one instance of another class. For example, a Person class might have a one-to-one relationship with a Passport class.
- **One-to-Many**: One instance of a class is associated with multiple instances of another class. For instance, a Teacher class may be associated with multiple Student objects.
- **Many-to-Many**: Many instances of a class are associated with many instances of another class. For example, a Student class might be associated with multiple Course objects, and each Course object can have multiple Students.

In most programming languages, association is implemented by referencing one class in another using pointers, references, or collections.

Consider the given code snippet:

```java
import java.util.*;

// One-to-One: a Person is associated with exactly one Passport.
class Passport {
    private String number;

    public Passport(String number) {
        this.number = number;
    }

    public String getNumber() {
        return number;
    }
}

class Person {
    private String name;
    private Passport passport; // a reference — the Passport is not owned by Person

    public Person(String name, Passport passport) {
        this.name = name;
        this.passport = passport;
    }

    public String getName() {
        return name;
    }

    public Passport getPassport() {
        return passport;
    }
}

// One-to-Many: one Teacher is associated with many Students.
class Student {
    private String name;

    public Student(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}

class Teacher {
    private String name;
    private List<Student> students; // a collection of references

    public Teacher(String name, List<Student> students) {
        this.name = name;
        this.students = students;
    }

    public void teach() {
        for (Student s : students) {
            System.out.println(name + " teaches " + s.getName());
        }
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        // One-to-One
        Passport passport = new Passport("P-4417");
        Person person = new Person("Alex", passport);
        System.out.println(person.getName() + " holds passport " + person.getPassport().getNumber());

        // One-to-Many
        List<Student> students = new ArrayList<>();
        students.add(new Student("Sam"));
        students.add(new Student("Riya"));
        Teacher teacher = new Teacher("Mrs. Rao", students);
        teacher.teach();

        // Both objects are merely linked — neither owns the other, so each can
        // outlive the relationship. That is what makes this association.
        System.out.println("Students still exist independently: " + students.size());
    }
}
```

**The same idea in Python**

```python
from typing import List


# One-to-One: a Person is associated with exactly one Passport.
class Passport:
    def __init__(self, number: str) -> None:
        self._number = number  # single underscore: "internal by convention" (no `private`)

    @property
    def number(self) -> str:
        return self._number


class Person:
    def __init__(self, name: str, passport: Passport) -> None:
        self._name = name
        self._passport = passport  # a reference — the Passport is not owned by Person

    @property
    def name(self) -> str:
        return self._name

    @property
    def passport(self) -> Passport:
        return self._passport


# One-to-Many: one Teacher is associated with many Students.
class Student:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class Teacher:
    def __init__(self, name: str, students: List[Student]) -> None:
        self._name = name
        self._students = students  # a collection of references

    def teach(self) -> None:
        for s in self._students:
            print(f"{self._name} teaches {s.name}")


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    # One-to-One
    passport = Passport("P-4417")
    person = Person("Alex", passport)
    print(f"{person.name} holds passport {person.passport.number}")

    # One-to-Many
    students = [Student("Sam"), Student("Riya")]
    teacher = Teacher("Mrs. Rao", students)
    teacher.teach()

    # Both objects are merely linked — neither owns the other, so each can
    # outlive the relationship. That is what makes this association.
    print(f"Students still exist independently: {len(students)}")
```

## Aggregation

Aggregation is a specialized form of association. It represents a "whole-part" relationship where the "whole" and "part" can exist independently. For example, a Department class may contain multiple Employee objects, but the employees can exist independently of the department.

Consider the following code snippet:

```java
import java.util.*;

// Department Class
class Department {
    private List<Employee> employees;

    public Department(List<Employee> employees) {
        this.employees = employees;
    }
}

// Employee Class
class Employee {
    private String name;

    public Employee(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        // The employees are created OUTSIDE the department and passed in.
        List<Employee> staff = new ArrayList<>();
        staff.add(new Employee("Alex"));
        staff.add(new Employee("Sam"));

        Department department = new Department(staff);
        System.out.println("Department created with " + staff.size() + " employees.");

        // Drop the department; the employees are untouched.
        department = null;
        System.out.println("Department deleted. Employees still alive:");
        for (Employee e : staff) {
            System.out.println("  " + e.getName());
        }
    }
}
```

**The same idea in Python**

```python
from typing import List


class Employee:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class Department:
    def __init__(self, employees: List[Employee]) -> None:
        self._employees = employees


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    # The employees are created OUTSIDE the department and passed in.
    staff = [Employee("Alex"), Employee("Sam")]

    department = Department(staff)
    print(f"Department created with {len(staff)} employees.")

    # Drop the department; the employees are untouched. Python has no
    # explicit "delete the object" statement like Java's `= null` — this
    # just drops the only reference to `department`, making it eligible
    # for garbage collection. `staff` still holds its own references.
    department = None
    print("Department deleted. Employees still alive:")
    for e in staff:
        print(f"  {e.name}")
```

In this example, Employee objects are aggregated into a Department object.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** Even if the Department object is deleted, the Employee objects can continue to exist.

</div>

### Characteristics of Aggregation

- **Independence**: The lifecycle of the "part" is not dependent on the "whole."
- **Weaker Bond**: The relationship is less tightly coupled compared to composition.

## Composition

Composition is a stricter form of aggregation where the "whole" and "part" are tightly coupled.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** If the "whole" is destroyed, the "parts" are also destroyed.

</div>

This represents a "part-of" relationship. For example, a House class might contain multiple Room objects. If the House is destroyed, the Room objects cease to exist.

Consider the given code snippet:

```java
import java.util.*;

class House {
    private List<Room> rooms;

    public House() {
        rooms = new ArrayList<>();
        rooms.add(new Room("Living Room"));
        rooms.add(new Room("Bedroom"));
    }

    public List<Room> getRooms() {
        return rooms;
    }
}

class Room {
    private String name;

    public Room(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        // The rooms are created INSIDE the House constructor — nothing outside
        // ever holds a reference to them.
        House house = new House();
        System.out.println("House built with these rooms:");
        for (Room r : house.getRooms()) {
            System.out.println("  " + r.getName());
        }

        // Drop the house and its rooms become unreachable with it — that is the
        // difference from aggregation.
        house = null;
        System.out.println("House destroyed — its rooms are unreachable and go with it.");
    }
}
```

**The same idea in Python**

```python
from typing import List


class Room:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class House:
    def __init__(self) -> None:
        # The rooms are created INSIDE the House constructor — nothing
        # outside ever holds a reference to them.
        self._rooms: List[Room] = [Room("Living Room"), Room("Bedroom")]

    @property
    def rooms(self) -> List[Room]:
        return self._rooms


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    house = House()
    print("House built with these rooms:")
    for r in house.rooms:
        print(f"  {r.name}")

    # Drop the house and its rooms become unreachable with it — that is the
    # difference from aggregation. (No `= null` in Python; reassigning to
    # None just drops the last reference, so the Rooms become collectible.)
    house = None
    print("House destroyed — its rooms are unreachable and go with it.")
```

Here, Room objects are part of the House object. If the House is destroyed, the Room objects are also destroyed.

### Characteristics of Composition

- **Dependency**: The lifecycle of the "part" is entirely dependent on the "whole."
- **Stronger Bond**: The relationship is tightly coupled.

## Multiple Types of Relationships

In real-world systems, a class can participate in multiple types of relationships simultaneously. For example:

- A Library class can have an aggregation relationship with a Book class (books can exist without the library).
- The Book class can have a composition relationship with a Chapter class (chapters cease to exist if the book is destroyed).

Understanding and identifying these relationships is crucial for designing systems that are both efficient and easy to maintain.

## Comparison Table

To summarize the differences between association, aggregation, and composition, the table below provides a concise overview:

| Aspect | Association | Aggregation | Composition |
| --- | --- | --- | --- |
| Relationship | General | Weak | Strong |
| Ownership | No ownership | One class contains another but does not own it | One class owns the other |
| Independence | Classes can exist independently | Contained class can exist independently | Contained class cannot exist independently |
| Real-world Example | Teacher and Student | Employee and Department | Car and Engine |

## Conclusion

Relationships between classes are the backbone of object-oriented design. By understanding association, aggregation, and composition, developers can model real-world systems with clarity and precision. Whether you’re designing a simple application or a complex system, mastering these concepts is essential for writing clean, maintainable, and robust code.

## Practice (Composition)

Design a system to manage a composition relationship between a University and its Colleges. Implement the following:

**University class :**

**Attribute:** colleges (List of College objects), name (string)

**Methods:**

- **addCollege(collegeName, collegeId)**: Adds a college to the university.
- **displayDetails()**: Prints the university's details along with all associated colleges.

**College Class :**

**Attributes:** name (String), id (String).

For output format refer the commented code on IDE.

**Example 1**

**Input :** name = "Global_University" ,

college Names = [ "COEP", "PICT", "VJTI", "WCE", "PCCOE" ]

college Id = [ "CO8543", "PI9514", "VJ8643", "VF569", "PC9246" ]

**Output :**

University Name : Global_University

College Name : COEP

College ID : CO8543

College Name : PICT

College ID : PI9514

College Name : VJTI

College ID : VJ8643

College Name : WCE

College ID : VF569

College Name : PCCOE

College ID : PC9246

**Explanation :**

1. First we create the object of class University with name as argument to constructor.
2. Then we call the method addCollege to add the mentioned college names and id under that university object.
3. Then the displayDetails method is called to display the content of the University and Colleges.

## Object Cloning

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Definition.** Object cloning refers to creating an exact copy (or a near-identical copy) of an object.

</div>

The cloned object has the same structure and data as the original but occupies a different memory location.
In Java, cloning is supported by the Cloneable interface and the Object class's clone() method.

**Key characteristics:**

- The cloned object is independent of the original object.
- Changes to the cloned object do not affect the original object (except in shallow cloning for reference types).

### Purpose behind using Object Cloning

Cloning is used for the following purposes:

- **Efficiency**: Instead of recreating and reinitializing an object from scratch, cloning allows the creation of a duplicate with minimal effort.
- **Reducing Coupling**: It ensures that changes to one object do not propagate unintentionally to another.
- **Preserving State**: Cloning helps preserve the current state of an object for tasks such as undo/redo operations or caching.
- **Working with Immutable Objects**: When you want to modify an object but cannot (e.g., immutable collections), cloning can create modifiable copies.
- **Prototyping**: In design patterns like the Prototype Pattern, cloning is frequently used to replicate objects.

### Working of Cloning

Cloning in Java is facilitated through the following components:

**1. The Cloneable Interface**

The Cloneable interface is a marker interface (it has no methods). Its purpose is to signal to the Java Virtual Machine (JVM) that the clone() method of a class is safe to invoke.

**2. The clone() Method**

The clone() method is defined in the Object class. By default, it performs a shallow copy of the object. When invoked, it:

- Allocates a new memory location for the cloned object.
- Copies the field values (primitives are copied, references are copied but not the objects they refer to).

### Types of Cloning

Cloning in Java can be categorized into two types:

- **Shallow Cloning**: Copies primitive fields and references for objects. The cloned object shares the same reference for nested objects.
- **Deep Cloning**: Creates a completely independent copy of the original object, including copies of all nested objects.

### Shallow Cloning

Shallow cloning creates a new object that is a duplicate of the original object but only at the surface level. The new object will have the same values for all primitive fields, and references to the same memory locations for any reference-type fields (e.g., objects, arrays, or collections).

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** This means that while the cloned object is distinct from the original, any modifications to shared references will be reflected in both objects.

</div>

Shallow cloning is done using clone() method.

Consider the following example:

```java
import java.util.*;

// Address class
class Address {
    String city;

    // Constructor
    Address(String city) {
        this.city = city;
    }
}

// Person class (which is clonable)
class Person implements Cloneable {
    String name; // Primitive field
    Address address; // Reference-type field

    // Constructor
    Person(String name, Address address) {
        this.name = name;
        this.address = address;
    }

    // clone() method is inherited from Object class and must be Overriden
    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();  // Shallow copy
    }
}

class Main {
    public static void main(String[] args) throws CloneNotSupportedException {
        Address address = new Address("Mumbai");
        Person person = new Person("Rahul", address);

        Person clonedPerson = (Person) person.clone(); // Cloning person

        // Modifying the address in the cloned object
        clonedPerson.address.city = "New Delhi";

        // Output to check if changes are reflected in the original
        System.out.println(person.name + " lives in " + person.address.city);
        System.out.println(clonedPerson.name + " lives in " + clonedPerson.address.city);
    }
}
```

**Output:**

```
Rahul lives in New Delhi
Rahul lives in New Delhi
```

**Breakdown of code:**

- **@Override Annotation**: This ensures that we are correctly overriding the clone() method from the Object class.
- **protected Object clone() Method**: The clone() method is inherited from the Object class and must be overridden to enable object cloning.
- **throws CloneNotSupportedException**: CloneNotSupportedException is thrown if the class does not implement the Cloneable interface. Java enforces this to prevent accidental cloning of objects that are not explicitly designed for cloning.
- **super.clone()**: Calls the clone() method from the Object class. This performs a shallow copy meaning:
  - Primitive fields (eg: String name) are copied as-is.
  - References to the References-fields (eg: Address address) are copied (not the objects themselves). This means that any changes in reference fields are reflected in the cloned objects.

**Explanation:**

- The cloned object clonedPerson gets a copy of person, but the address field is shared.
- Changing clonedPerson.address.city also changes person.address.city, proving that the object reference is shared.
- This is a key limitation of shallow cloning.

### Deep Cloning

Deep cloning ensures that a completely independent copy of the object is created, including all nested objects. This prevents unintended modifications in the original object when the cloned object is modified.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** Since the default clone() method performs a shallow copy, deep cloning requires manual cloning of all referenced objects.

</div>

This can be done using the clone() method recursively.

Consider the following example:

```java
import java.util.*;
// Address class (which is cloneable)
class Address implements Cloneable {
    String city;

    // Constructor
    Address(String city) {
        this.city = city;
    }

    // Overriding default clone() method
    @Override
    protected Object clone() throws CloneNotSupportedException {
        return new Address(this.city);  // Creating a new object
    }
}


// Person class which is cloneable
class Person implements Cloneable {
    String name; // Primitive field
    Address address; // Reference-type field

    // Constructor
    Person(String name, Address address) {
        this.name = name;
        this.address = address;
    }

    // Overriding
    @Override
    protected Object clone() throws CloneNotSupportedException {
        Person clonedPerson = (Person) super.clone(); // Shallow copy

        // Cloning nested object for Deep Cloning
        clonedPerson.address = (Address) address.clone();
        return clonedPerson;
    }
}

class Main {
    public static void main(String[] args) throws CloneNotSupportedException {
        Address address = new Address("Mumbai");
        Person person = new Person("Rahul", address);

        Person clonedPerson = (Person) person.clone(); // Deep Cloning

        // Modifying the address in the cloned object
        clonedPerson.address.city = "New Delhi";

        // Output to check if changes are reflected in the original
        System.out.println(person.name + " lives in " + person.address.city);  // Mumbai
        System.out.println(clonedPerson.name + " lives in " + clonedPerson.address.city);  // New Delhi
    }
}
```

**Output:**

```
Rahul lives in Mumbai
Rahul lives in New Delhi
```

**Breakdown of code:**

- **@Override Annotation:**
  - This ensures that we are correctly overriding the clone() method from the Object class.
  - Used in both Person and Address classes to override the clone() method.
- **protected Object clone() Method in Person:**
  - The clone() method is inherited from the Object class and must be overridden to enable object cloning.
  - Calls super.clone() for a shallow copy but additionally clones the Address object manually for Deep Cloning.
- **throws CloneNotSupportedException**: CloneNotSupportedException is thrown if the class does not implement the Cloneable interface. Java enforces this to prevent accidental cloning of objects that are not explicitly designed for cloning.
- **super.clone()**: Calls the clone() method from the Object class. This performs a shallow copy. This behaviour is modified by cloning the Address object manually.

**Why overriding clone() in Address class is required for Deep Cloning?**

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** If Address did not override clone(), clonedPerson.address = (Address) address.clone(); would fail.

</div>

This also ensures each Person object has its own independent Address object.

**Explanation:**

- The cloned object clonedPerson gets a copy of person, and the Address field is cloned manually.
- Changing person.address.city does not change clonedPerson.address.city, proving that the object reference is not shared.

### Shallow Cloning vs Deep Cloning

| Aspect | Shallow Cloning | Deep Cloning |
| --- | --- | --- |
| Copies Primitive Fields | Yes | Yes |
| Copies Object References | No (shares references) | Yes (creates separate objects) |
| Requires Overriding in Nested Objects? | No | Yes |
| Independent Nested Objects? | No | Yes |
| Use Case | When objects have only primitive fields | When objects have references to other mutable objects |

#### The same idea in Python

Python has no `Cloneable` interface and no `clone()` method to override — the standard library's
`copy` module does the job generically for any object: `copy.copy()` performs a shallow copy,
`copy.deepcopy()` performs a deep copy (recursively, including cyclic references). The driver below
reproduces both Person/Address examples above in one program, so the original/shallow/deep
divergence is visible side by side exactly as it is across the two Java examples.

```python
import copy


class Address:
    def __init__(self, city: str) -> None:
        self.city = city


class Person:
    def __init__(self, name: str, address: Address) -> None:
        self.name = name
        self.address = address


# ── Driver ──────────────────────────────────────────────
if __name__ == "__main__":
    address = Address("Mumbai")
    person = Person("Rahul", address)

    # Shallow clone: copy.copy() duplicates the Person but reuses the SAME
    # Address object underneath, just like Java's default super.clone().
    shallow_clone = copy.copy(person)
    shallow_clone.address.city = "New Delhi"
    print(f"{person.name} lives in {person.address.city}")            # Mumbai -> New Delhi (shared)
    print(f"{shallow_clone.name} lives in {shallow_clone.address.city}")

    # Reset the shared Address before demonstrating the deep-clone half.
    person.address.city = "Mumbai"

    # Deep clone: copy.deepcopy() recursively duplicates every nested
    # object too, so the two Address instances end up fully independent —
    # no manual per-field clone() overrides required, unlike Java.
    deep_clone = copy.deepcopy(person)
    deep_clone.address.city = "New Delhi"
    print(f"{person.name} lives in {person.address.city}")            # stays Mumbai
    print(f"{deep_clone.name} lives in {deep_clone.address.city}")
```

## Practice (Object Cloning)

You are required to design a class hierarchy to demonstrate object cloning using shallow and deep copying in a library system. A Library contains a list of Book objects.

- **Shallow Copy**: Creates a new object that shares references with the original object for nested structures.
- **Deep Copy**: Creates a completely independent copy of the original object, including all nested structures.

**Classes :**

**Book :**

**Attributes :** title (string) , author (string)

**Library :**

**Attributes :** name (string) , books (List of Book class)

**Methods :**

- **shallowClone()**: Creates a shallow copy of the Library object.
- **deepClone()**: Creates a deep copy of Library object.
- **display()**: Displays the output/ attributes of the class.
- **addBook (Book book)**: It adds one book info to the list of books.

Refer the commented code on IDE to understand the output format using display method.

Refer the sample example output to understand the output format.

**Example 1**

**Input:**

```text
name = "Central_Library"
title = [ "Frankestein", "King_Arthur_and_the_Round_Table" ]
author = [ "Mary_Shelley", "Rosemary_Sutcliff" ]
changeIndex = 1
newTitle = "Treasure_Island"
new_author = "Robert_Louis_Stevenson"
```

**Output:**

```text
Original Library :
Library : Central_Library
Book : Frankestein, Author : Mary_Shelley
Book : King_Arthur_and_the_Round_Table, Author : Rosemary_Sutcliff

After Modifications :
Library : Central_Library
Book : Frankestein, Author : Mary_Shelley
Book : Treasure_Island, Author : Robert_Louis_Stevenson

Shallow Clone :
Library : Central_Library
Book : Frankestein, Author : Mary_Shelley
Book : Treasure_Island, Author : Robert_Louis_Stevenson

Deep Clone :
Library : Central_Library
Book : Frankestein, Author : Mary_Shelley
Book : King_Arthur_and_the_Round_Table, Author : Rosemary_Sutcliff
```

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** As per output you can see, that the title and author for book at index = 1, have been changed in original library object and shallow clone object. But whereas the Deep clone object still has the old information.

</div>

**Explanation :**

1. First we will create a Library class object named 'library' with name being passed through constructor for initialization.
2. Then we will iterate over the title and author array to add them in the list of books present in the Library class.
3. Now a text is printed through driver code. And following it we call the display function of Library class to print the attributes of the library object that we set.
4. Next we will create the shallow clone object by calling the method shallowClone().
5. Next we will create the deep clone object by calling the method deepClone().
6. Now we will change the title and author of the index 'changeIndex' to newTitle and newAuthor for the original library object. (This will be done through driver code, you do not have to write this part).
7. Now we will print some text and call the display method through the original library object and print the attributes of Library class.
8. Next we will call the display method through shallow clone object and print the attributes of Library class.
9. Next we will call the display method through deep clone object and print the attributes of Library class.
10. As per output you can see, that the title and author for book at index = 1, have been changed in original library object and shallow clone object. But whereas the Deep clone object still has the old information.

This is what you should be able to achieve through your code.

**Constraints**

- 1 <= title.size() , author.size() <= 104
- title.size() == author.size()
- 0 <= changeIndex < title.size()

**Solution**

```java
import java.util.*;

// Book class supports cloning
class Book implements Cloneable {
    String title;
    String author;

    // Constructor to initialize book details
    Book(String title, String author) {
        this.title = title;
        this.author = author;
    }

    @Override
    protected Book clone() throws CloneNotSupportedException {
        // default shallow copy (safe since String is immutable)
        return (Book) super.clone();
    }
}


// Library class supports shallow and deep cloning
class Library implements Cloneable {
    String name;
    List<Book> books;

    // Initialize library with empty book list
    Library(String name) {
        this.name = name;
        this.books = new ArrayList<>();
    }

    // Add a book to the library
    void addBook(Book book) {
        books.add(book);
    }

    // Shallow clone → shares same books list reference
    Library shallowClone() throws CloneNotSupportedException {
        // list reference copied, not duplicated
        return (Library) super.clone();
    }

    // Deep clone → creates new list + new Book objects
    Library deepClone() throws CloneNotSupportedException {
        // copy primitive + references first
        Library cloned = (Library) super.clone();

        cloned.books = new ArrayList<>(); // create independent list

        for (Book book : this.books) {
            cloned.books.add(book.clone()); // clone each book separately
        }

        return cloned;
    }

    // Display library details
    void display() {
        System.out.println("Library : " + name);
        for (Book book : books) {
            System.out.println("Book : " + book.title + ", Author : " + book.author);
        }
    }
}

class Main {
    public static void main(String[] args) throws CloneNotSupportedException {
        // Hardcoded input
        String libraryName = "Central_Library";
        String[] titles = { "Frankestein", "King_Arthur_and_the_Round_Table" };
        String[] authors = { "Mary_Shelley", "Rosemary_Sutcliff" };
        int changeIndex = 1;
        String newTitle = "Treasure_Island";
        String newAuthor = "Robert_Louis_Stevenson";

        // Create library and add books
        Library library = new Library(libraryName);
        for (int i = 0; i < titles.length; i++) {
            library.addBook(new Book(titles[i], authors[i]));
        }

        // Display original library
        System.out.println("Original Library :");
        library.display();

        // Create the clones BEFORE modifying, so the deep clone captures the original state
        Library shallowClonedLibrary = library.shallowClone();
        Library deepClonedLibrary = library.deepClone();

        // Modify the book at changeIndex on the original library
        library.books.get(changeIndex).title = newTitle;
        library.books.get(changeIndex).author = newAuthor;

        System.out.println("\nAfter Modifications :");
        library.display();

        // Display shallow clone — it shares the books list, so it reflects the change
        System.out.println("\nShallow Clone :");
        shallowClonedLibrary.display();

        // Display deep clone — it is independent, so it keeps the original data
        System.out.println("\nDeep Clone :");
        deepClonedLibrary.display();
    }
}
```
