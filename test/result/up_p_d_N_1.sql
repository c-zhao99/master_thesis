CREATE TABLE Employee (
    EmployeeID {ADD_TYPE} NOT NULL,
    TeamName {ADD_TYPE},
    Level {ADD_TYPE},
    Product {ADD_TYPE},
    TYPE_ManagerEngineerProductManager VARCHAR(50) NOT NULL CHECK (TYPE_ManagerEngineerProductManager IN (['Manager', 'Engineer', 'ProductManager', 'Employee'])),
    Promote_Manager_EmployeeID {ADD_TYPE} UNIQUE REFERENCES Employee(EmployeeID),
    Manage_Manager_EmployeeID {ADD_TYPE} UNIQUE REFERENCES Employee(EmployeeID),
    PRIMARY KEY (EmployeeID),
    CONSTRAINT ManagerEngineerProductManager CHECK ((TYPE_ManagerEngineerProductManager = Manager AND TeamName IS NOT NULL AND Promote_Manager_EmployeeID IS NULL AND Level IS NULL AND Product IS NULL) OR (TYPE_ManagerEngineerProductManager = Engineer AND Level IS NOT NULL AND Promote_Manager_EmployeeID IS NOT NULL AND TeamName IS NULL AND Product IS NULL) OR (TYPE_ManagerEngineerProductManager = ProductManager AND Product IS NOT NULL AND Promote_Manager_EmployeeID IS NULL AND TeamName IS NULL AND Level IS NULL) OR (TYPE_ManagerEngineerProductManager = Employee AND TeamName IS NULL AND Level IS NULL AND Product IS NULL AND Promote_Manager_EmployeeID IS NULL))
);


CREATE TABLE Customer (
    CustomerID {ADD_TYPE} NOT NULL,
    Interact_ProductManager_EmployeeID {ADD_TYPE} UNIQUE REFERENCES Employee(EmployeeID),
    PRIMARY KEY (CustomerID)
);


CREATE TABLE PlanWith (
    Year {ADD_TYPE} NOT NULL,
    PlanWith_Manager_EmployeeID_A {ADD_TYPE} UNIQUE NOT NULL REFERENCES Employee(EmployeeID),
    PlanWith_Manager_EmployeeID_B {ADD_TYPE} UNIQUE NOT NULL REFERENCES Employee(EmployeeID),
    PRIMARY KEY (PlanWith_Manager_EmployeeID_A,PlanWith_Manager_EmployeeID_B)
);


CREATE TRIGGER PlanWithManager
BEFORE INSERT ON PlanWith
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    N.TYPE_ManagerEngineerProductManager = Manager AND NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.PlanWith_Manager_EmployeeID_A
        AND Employee.TYPE_ManagerEngineerProductManager = Manager
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of Manager!')

CREATE TRIGGER PlanWithManager
BEFORE INSERT ON PlanWith
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    N.TYPE_ManagerEngineerProductManager = Manager AND NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.PlanWith_Manager_EmployeeID_B
        AND Employee.TYPE_ManagerEngineerProductManager = Manager
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of Manager!')

CREATE TRIGGER PromoteManager
BEFORE INSERT ON Employee
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    N.TYPE_ManagerEngineerProductManager = Engineer AND NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.Promote_Manager_EmployeeID
        AND Employee.TYPE_ManagerEngineerProductManager = Manager
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of Manager!')

CREATE TRIGGER ManageManager
BEFORE INSERT ON Employee
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.Manage_Manager_EmployeeID
        AND Employee.TYPE_ManagerEngineerProductManager = Manager
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of Manager!')

CREATE TRIGGER InteractProductManager
BEFORE INSERT ON Customer
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.Interact_ProductManager_EmployeeID
        AND Employee.TYPE_ManagerEngineerProductManager = ProductManager
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of ProductManager!')