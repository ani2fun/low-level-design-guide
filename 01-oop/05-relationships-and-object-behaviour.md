---
title: "Relationships and Object Behaviour"
summary: "How classes connect through association, aggregation, and composition, and how objects are duplicated through shallow and deep cloning — with worked examples and practice problems."
essential: true
---

# Relationships and Object Behaviour

In object-oriented programming (OOP), classes are the foundational building blocks that define the structure and behaviour of objects. One of the most important concepts in OOP is how these classes interact with each other.

These interactions, or relationships, allow developers to model real-world systems effectively. This article delves into the key types of relationships between classes: association, aggregation, and composition. They are the arrows of a UML class diagram, and the reason [composition is often preferred over inheritance](/synapse/low-level-design/oop/encapsulation-access-modifiers-inheritance-polymorphism).

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **The core idea.** Objects rarely work alone. They collaborate. The strength of the bond between collaborating objects — from a passing reference to strict ownership — determines how their lifecycles intertwine and how changes cascade through a system.

</div>

**You'll be able to:**
- Distinguish between association, aggregation, and composition.
- Model object relationships with appropriate lifecycle ownership.
- Duplicate objects using shallow and deep cloning.
- Avoid common pitfalls with shared references and `Cloneable`.

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **How to read the Intuition boxes.** As you read, look for the *Mechanism* and *Concrete bite* under each code block. They map the code you just saw to the mental model you need to build.

</div>

1. [Association: linking without ownership](#1-association-linking-without-ownership)
2. [Aggregation: whole-part with independent lifecycles](#2-aggregation-whole-part-with-independent-lifecycles)
3. [Composition: whole-part with a shared lifecycle](#3-composition-whole-part-with-a-shared-lifecycle)
4. [Shallow vs deep cloning (and the Cloneable trap)](#4-shallow-vs-deep-cloning-and-the-cloneable-trap)

## 1. Association: linking without ownership

Association defines how two classes are connected. It represents a situation where objects of one class interact with objects of another through some form of linkage or reference. The connection can be one-to-one, one-to-many, or many-to-many, enabling different levels of collaboration and data sharing between the classes.

In most programming languages, association is implemented by referencing one class in another using pointers, references, or collections.

```java run
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
```python run
from typing import List

# One-to-One: a Person is associated with exactly one Passport.
class Passport:
    def __init__(self, number: str) -> None:
        self._number = number

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

**Output:**
```
Alex holds passport P-4417
Mrs. Rao teaches Sam
Mrs. Rao teaches Riya
Students still exist independently: 2
```

**Analysis.** The `Person` class has a `passport` field, and the `Teacher` class has a list of `students`. The objects refer to one another, but there is no strict ownership or lifecycle dependence.

**Intuition.**
- **Mechanism.** Association is the most general relationship. Object A simply knows about Object B by holding a reference to it.
- **Concrete bite.** A `Teacher` teaches a `Student`, but the `Student` exists before the `Teacher` is assigned and continues to exist after the `Teacher` retires. They are independent entities that temporarily collaborate.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use association when two classes need to interact, but neither logically owns the other. The objects have independent lifecycles.

</div>

## 2. Aggregation: whole-part with independent lifecycles

Aggregation is a specialized form of association. It represents a "whole-part" relationship where the "whole" and "part" can exist independently. For example, a `Department` class may contain multiple `Employee` objects, but the employees can exist independently of the department.

```java run
import java.util.*;

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

// Department Class
class Department {
    private List<Employee> employees;

    public Department(List<Employee> employees) {
        this.employees = employees;
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
```python run
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

**Output:**
```
Department created with 2 employees.
Department deleted. Employees still alive:
  Alex
  Sam
```

**Analysis.** In this example, `Employee` objects are aggregated into a `Department` object. Because the `Employee` instances are created outside the `Department` and passed in via the constructor, they are not owned by the `Department`. When the `department` variable is set to `null` (or `None` in Python), the `Department` is destroyed, but the `staff` list and its `Employee` objects remain perfectly intact.

**Intuition.**
- **Mechanism.** Aggregation is a "has-a" relationship with a weak bond. The containing object holds references to the contained objects, but it does not control their lifecycle.
- **Concrete bite.** A `Department` has `Employees`. If the company closes the `Department`, the `Employees` are not destroyed; they are reassigned.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use aggregation when an object acts as a container or collection of other objects, but those objects make sense outside the context of the container.

</div>

## 3. Composition: whole-part with a shared lifecycle

Composition is a stricter form of aggregation where the "whole" and "part" are tightly coupled. This represents a "part-of" relationship. If the "whole" is destroyed, the "parts" are also destroyed.

```java run
import java.util.*;

class Room {
    private String name;

    public Room(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}

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
```python run
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

**Output:**
```
House built with these rooms:
  Living Room
  Bedroom
House destroyed — its rooms are unreachable and go with it.
```

**Analysis.** The `Room` instances are created *inside* the `House` constructor. Because no external code holds a reference to them initially, they are strictly owned by the `House`. When the `House` is destroyed (by dropping the only reference to it), the `Room` objects are also garbage collected.

**Intuition.**
- **Mechanism.** Composition is a "part-of" relationship with a strong bond. The containing object creates and manages the lifecycle of the contained objects.
- **Concrete bite.** A `House` is composed of `Rooms`. If you demolish the `House`, the `Rooms` cease to exist. A `Room` does not make sense as a standalone entity without a `House`.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Use composition when a contained object is conceptually a piece of the container, and should not outlive the container. The container is strictly responsible for creating the part.

</div>

<div style="border-left:4px solid #15448e;background:rgba(21,68,142,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

📘 **Info.** In real-world systems, a class can participate in multiple types of relationships simultaneously. For example, a `Library` class can have an aggregation relationship with a `Book` class (books can exist without the library), while the `Book` class can have a composition relationship with a `Chapter` class (chapters cease to exist if the book is destroyed).

</div>

````problem
```java run
```
```testcases
[
  {
    "input": "Global_University\n5\nCOEP CO8543\nPICT PI9514\nVJTI VJ8643\nWCE VF569\nPCCOE PC9246\n",
    "output": "University Name : Global_University\nCollege Name : COEP\nCollege ID : CO8543\nCollege Name : PICT\nCollege ID : PI9514\nCollege Name : VJTI\nCollege ID : VJ8643\nCollege Name : WCE\nCollege ID : VF569\nCollege Name : PCCOE\nCollege ID : PC9246\n"
  }
]
```
```editorial
Design a system to manage a composition relationship between a `University` and its `College`s. 

Implement the following:

**University class:**
- **Attribute:** `colleges` (List of College objects), `name` (string)
- **Methods:**
  - `addCollege(collegeName, collegeId)`: Adds a college to the university.
  - `displayDetails()`: Prints the university's details along with all associated colleges.

**College Class:**
- **Attributes:** `name` (String), `id` (String).

Ensure the output matches the expected format shown in the driver code.

### Constraints
- $1 \le N \le 100$ where N is the number of colleges
```
```java solution
import java.util.*;

// College class representing a part of the University
class College {
    private String name;
    private String id;

    public College(String name, String id) {
        this.name = name;
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public String getId() {
        return id;
    }
}

// University class representing the whole (Composition)
class University {
    private String name;
    private List<College> colleges;

    public University(String name) {
        this.name = name;
        // The University strictly owns the colleges list
        this.colleges = new ArrayList<>();
    }

    public void addCollege(String collegeName, String collegeId) {
        // The University creates the College instances, establishing strict ownership
        colleges.add(new College(collegeName, collegeId));
    }

    public void displayDetails() {
        System.out.println("University Name : " + name);
        for (College college : colleges) {
            System.out.println("College Name : " + college.getName());
            System.out.println("College ID : " + college.getId());
        }
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        if (!scanner.hasNextLine()) return;

        String universityName = scanner.nextLine().trim();
        int numColleges = Integer.parseInt(scanner.nextLine().trim());

        University university = new University(universityName);

        for (int i = 0; i < numColleges; i++) {
            String[] parts = scanner.nextLine().trim().split("\\s+");
            if (parts.length >= 2) {
                university.addCollege(parts[0], parts[1]);
            }
        }

        university.displayDetails();
    }
}
```
````

## 4. Shallow vs deep cloning (and the Cloneable trap)

Object cloning refers to creating an exact copy (or a near-identical copy) of an object. The cloned object has the same structure and data as the original but occupies a different memory location.

Copying only makes sense once you know that a variable holds a *reference* to an object, not the object itself. If that is new, read the Java guide's [References, Equality & the Object Model](/synapse/programming-languages/java/classes-and-objects/references-equality-and-the-object-model) first.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Design note.** `Cloneable` and `clone()` are easy to get wrong: `clone()` bypasses constructors, and every mutable field must be copied by hand. In new designs, prefer a **copy constructor** (`new Address(other)`) or a static copy factory, or make the class immutable so it never needs copying. This section explains `clone()` because you will meet it in existing code.

</div>

In Java, cloning is supported by the `Cloneable` interface and the `Object` class's `clone()` method. The `Cloneable` interface is a marker interface (it has no methods). Its purpose is to signal to the Java Virtual Machine (JVM) that the `clone()` method of a class is safe to invoke. If a class does not implement `Cloneable`, calling `super.clone()` throws a `CloneNotSupportedException`.

There are two main approaches to cloning:

1. **Shallow Cloning**: Copies primitive fields and references for objects. The cloned object shares the same reference for nested objects.
2. **Deep Cloning**: Creates a completely independent copy of the original object, including copies of all nested objects.

### Shallow Cloning

Shallow cloning creates a new object that is a duplicate of the original object but only at the surface level. The new object will have the same values for all primitive fields, and references to the same memory locations for any reference-type fields.

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Watch out.** This means that while the cloned object is distinct from the original, any modifications to shared references will be reflected in both objects.

</div>

```java run
import java.util.*;

// Address class
class Address {
    String city;

    Address(String city) {
        this.city = city;
    }
}

// Person class (which is clonable)
class Person implements Cloneable {
    String name;
    Address address; // Reference-type field

    Person(String name, Address address) {
        this.name = name;
        this.address = address;
    }

    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();  // Shallow copy
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) throws CloneNotSupportedException {
        Address address = new Address("Mumbai");
        Person person = new Person("Rahul", address);

        Person clonedPerson = (Person) person.clone(); // Shallow cloning

        // Modifying the shared address in the cloned object
        clonedPerson.address.city = "New Delhi";

        System.out.println(person.name + " lives in " + person.address.city);
        System.out.println(clonedPerson.name + " lives in " + clonedPerson.address.city);
    }
}
```
```python run
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
    
    # Modifying the shared address in the cloned object
    shallow_clone.address.city = "New Delhi"
    
    # Mumbai -> New Delhi (shared)
    print(f"{person.name} lives in {person.address.city}")            
    print(f"{shallow_clone.name} lives in {shallow_clone.address.city}")
```

**Output:**
```
Rahul lives in New Delhi
Rahul lives in New Delhi
```

**Analysis.** Calling `super.clone()` in Java or `copy.copy()` in Python creates a shallow copy. The primitive string `name` is copied, but the `address` field holds a reference to the exact same `Address` object in memory. When the cloned `Person` modifies the city, the original `Person` also sees the modification because there is only one `Address` instance.

### Deep Cloning

Deep cloning ensures that a completely independent copy of the object is created, including all nested objects. This prevents unintended modifications in the original object when the cloned object is modified. Since the default `clone()` method performs a shallow copy, deep cloning requires manual cloning of all referenced objects in Java.

```java run
import java.util.*;

// Address class (which is cloneable)
class Address implements Cloneable {
    String city;

    Address(String city) {
        this.city = city;
    }

    @Override
    protected Object clone() throws CloneNotSupportedException {
        return new Address(this.city);  // Creating a new independent object
    }
}

// Person class which is cloneable
class Person implements Cloneable {
    String name;
    Address address;

    Person(String name, Address address) {
        this.name = name;
        this.address = address;
    }

    @Override
    protected Object clone() throws CloneNotSupportedException {
        Person clonedPerson = (Person) super.clone(); // Shallow copy

        // Cloning nested object manually for Deep Cloning
        clonedPerson.address = (Address) address.clone();
        return clonedPerson;
    }
}

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) throws CloneNotSupportedException {
        Address address = new Address("Mumbai");
        Person person = new Person("Rahul", address);

        Person clonedPerson = (Person) person.clone(); // Deep Cloning

        // Modifying the independent address in the cloned object
        clonedPerson.address.city = "New Delhi";

        System.out.println(person.name + " lives in " + person.address.city);
        System.out.println(clonedPerson.name + " lives in " + clonedPerson.address.city);
    }
}
```
```python run
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

    # Deep clone: copy.deepcopy() recursively duplicates every nested
    # object too, so the two Address instances end up fully independent —
    # no manual per-field clone() overrides required, unlike Java.
    deep_clone = copy.deepcopy(person)
    
    # Modifying the independent address in the cloned object
    deep_clone.address.city = "New Delhi"
    
    print(f"{person.name} lives in {person.address.city}")
    print(f"{deep_clone.name} lives in {deep_clone.address.city}")
```

**Output:**
```
Rahul lives in Mumbai
Rahul lives in New Delhi
```

**Analysis.** In Java, `Person.clone()` calls `super.clone()` for the primitive fields, and then explicitly calls `address.clone()` to create a new `Address` instance. In Python, `copy.deepcopy()` handles the recursion automatically. Because the cloned `Person` has its own isolated `Address` object, modifying its city does not affect the original `Person`.

**Intuition.**
- **Mechanism.** Shallow copying shares nested references. Deep copying duplicates the entire object graph recursively.
- **Concrete bite.** If you copy a document that contains a link to an image, a shallow copy copies the link (both documents load the same image). A deep copy downloads a separate copy of the image and links to the new copy.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Earned rule.** Only use shallow cloning if all fields in a class are primitive or strictly immutable (like `String`). If a class contains mutable references, you must write a deep copy to prevent shared state bugs.

</div>

````problem
```java run
```
```testcases
[
  {
    "input": "Central_Library\n2\nFrankestein Mary_Shelley\nKing_Arthur_and_the_Round_Table Rosemary_Sutcliff\n1 Treasure_Island Robert_Louis_Stevenson\n",
    "output": "Original Library :\nLibrary : Central_Library\nBook : Frankestein, Author : Mary_Shelley\nBook : King_Arthur_and_the_Round_Table, Author : Rosemary_Sutcliff\n\nAfter Modifications :\nLibrary : Central_Library\nBook : Frankestein, Author : Mary_Shelley\nBook : Treasure_Island, Author : Robert_Louis_Stevenson\n\nShallow Clone :\nLibrary : Central_Library\nBook : Frankestein, Author : Mary_Shelley\nBook : Treasure_Island, Author : Robert_Louis_Stevenson\n\nDeep Clone :\nLibrary : Central_Library\nBook : Frankestein, Author : Mary_Shelley\nBook : King_Arthur_and_the_Round_Table, Author : Rosemary_Sutcliff\n"
  }
]
```
```editorial
You are required to design a class hierarchy to demonstrate object cloning using shallow and deep copying in a library system. A Library contains a list of Book objects.

- **Shallow Copy**: Creates a new object that shares references with the original object for nested structures.
- **Deep Copy**: Creates a completely independent copy of the original object, including all nested structures.

**Classes:**

**Book:**
- **Attributes:** `title` (string), `author` (string)

**Library:**
- **Attributes:** `name` (string), `books` (List of Book class)
- **Methods:**
  - `shallowClone()`: Creates a shallow copy of the Library object.
  - `deepClone()`: Creates a deep copy of Library object.
  - `display()`: Displays the output/attributes of the class.
  - `addBook(Book book)`: Adds one book to the list of books.

<div style="border-left:4px solid #195045;background:rgba(25,80,69,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

💡 **Insight.** As per output you can see, that the title and author for book at index = 1, have been changed in original library object and shallow clone object. But whereas the Deep clone object still has the old information.

</div>

### Explanation of the Driver flow
1. Create a `Library` class object.
2. Iterate over the title and author array to add them in the list of books.
3. Call `display()` on the original library.
4. Create a shallow clone object.
5. Create a deep clone object.
6. Change the title and author of the index 'changeIndex' to newTitle and newAuthor for the original library object.
7. Call `display()` on the original library.
8. Call `display()` on the shallow clone object. (It reflects the changes).
9. Call `display()` on the deep clone object. (It does not reflect the changes).
```
```java solution
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

// ── Driver ──────────────────────────────────────────────
class Main {
    public static void main(String[] args) throws CloneNotSupportedException {
        Scanner scanner = new Scanner(System.in);
        if (!scanner.hasNextLine()) return;

        String libraryName = scanner.nextLine().trim();
        int numBooks = Integer.parseInt(scanner.nextLine().trim());

        Library library = new Library(libraryName);
        for (int i = 0; i < numBooks; i++) {
            String[] parts = scanner.nextLine().trim().split("\\s+");
            if (parts.length >= 2) {
                library.addBook(new Book(parts[0], parts[1]));
            }
        }

        String[] changeParts = scanner.nextLine().trim().split("\\s+");
        int changeIndex = Integer.parseInt(changeParts[0]);
        String newTitle = changeParts[1];
        String newAuthor = changeParts[2];

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
````

## Summary

| Concept | Ownership | Lifecycle dependence | Example |
|---|---|---|---|
| **Association** | None | Independent | Teacher and Student |
| **Aggregation** | Loose | Independent | Department and Employee |
| **Composition** | Strict | Shared (whole kills part) | House and Room |
| **Shallow Clone** | Shared references | Changes to nested objects propagate | Copying a folder shortcut |
| **Deep Clone** | Separate references | Fully independent copies | Copying a folder's contents |

## 🚨 Gotcha Checklist
| Symptom | Likely cause | Fix |
|---|---|---|
| A modified cloned object unexpectedly changes the original object. | **Shallow copy leak.** Your `clone()` method returned `super.clone()` without duplicating nested mutable references. | Recursively clone mutable fields in your `clone()` method, or use a copy constructor. |
| `CloneNotSupportedException` thrown at runtime. | **Missing interface.** You called `super.clone()` but the class doesn't implement `Cloneable`. | Add `implements Cloneable` to the class declaration (a marker interface). |
| Garbage collection doesn't free "deleted" objects. | **Lingering association.** You dropped the main object, but a collection or another class still holds a reference to the child objects. | Clear the collection or explicitly drop references if lifecycle isn't strictly controlled via composition. |

<div style="border-left:4px solid #da5233;background:rgba(218,82,51,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

⚠️ **Anti-pattern: Leaking internal components.**
If a `House` owns its `Rooms` (composition), returning a direct reference to the internal list of rooms `public List<Room> getRooms() { return this.rooms; }` breaks encapsulation. External code could clear the list or add rooms, violating the House's lifecycle control. Instead, return an unmodifiable view: `return Collections.unmodifiableList(rooms);`.

</div>

## ✅ Check yourself

```quiz
{
  "prompt": "Which relationship represents strict ownership where destroying the container also destroys the contained objects?",
  "options": [
    "Association",
    "Aggregation",
    "Composition",
    "Dependency"
  ],
  "answer": "Composition"
}
```

```quiz
{
  "prompt": "If `ClassA` implements `Cloneable` and contains a mutable `List<String> items`, what does `super.clone()` do?",
  "options": [
    "It creates a deep copy of the items list.",
    "It throws CloneNotSupportedException because List is mutable.",
    "It creates a new List instance but points to the original strings.",
    "It creates a shallow copy, meaning the cloned object shares the exact same items list reference."
  ],
  "answer": "It creates a shallow copy, meaning the cloned object shares the exact same items list reference."
}
```

<details>
<summary>If aggregation and association both allow independent lifecycles, what is the practical difference?</summary>

**Association** is a broad relationship where objects simply know about each other (like a `Teacher` holding a reference to `Student`). **Aggregation** is a specialized "has-a" or "whole-part" association where one object acts as a container for others (like a `Department` holding a list of `Employee`s). In code, they often look identical (a list of references). The difference is conceptual and communicates design intent to other programmers: aggregation implies a grouping, while association just implies interaction.
</details>

## 📚 Sources
- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.
- Bloch, J. (2018). *Effective Java* (3rd ed.). Addison-Wesley Professional. (See Item 13: Override clone judiciously).

<div style="border-left:4px solid #8e155c;background:rgba(142,21,92,0.08);padding:0.6rem 1rem;border-radius:0 0.5rem 0.5rem 0;margin:1.25rem 0">

🧪 **Predict, then check.** 
If `Person` has a final `Address` field (`private final Address address;`), can you deep clone it in a `clone()` override by doing `cloned.address = (Address) this.address.clone();`? 

No. Final fields cannot be reassigned after construction. This is a major limitation of `Cloneable` and the reason Joshua Bloch recommends copy constructors over `clone()` in *Effective Java*.

</div>

## Your Turn

Look at the `University` and `College` classes you built in the first practice problem. If a `College` can technically be disaffiliated from one `University` and absorbed by another, does `Composition` still accurately model reality? How would you refactor the code if you changed the design to `Aggregation`? (Hint: Think about where the `new College()` calls happen).
