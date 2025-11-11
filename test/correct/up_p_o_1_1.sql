CREATE TABLE Employee (
    EmployeeID {ADD_TYPE} NOT NULL,
    TeamName {ADD_TYPE},
    Level {ADD_TYPE},
    Product {ADD_TYPE},
    TYPE_Manager VARCHAR(50) NOT NULL CHECK (TYPE_Manager IN (['0', '1'])),
    TYPE_Engineer VARCHAR(50) NOT NULL CHECK (TYPE_Engineer IN (['0', '1'])),
    TYPE_ProductManager VARCHAR(50) NOT NULL CHECK (TYPE_ProductManager IN (['0', '1'])),
    Promote_Manager_EmployeeID {ADD_TYPE} UNIQUE REFERENCES Employee(EmployeeID),
    Manage_Manager_EmployeeID {ADD_TYPE} UNIQUE REFERENCES Employee(EmployeeID),
    Interact_Customer_CustomerID {ADD_TYPE} UNIQUE REFERENCES Customer(CustomerID),
    PRIMARY KEY (EmployeeID),
    CONSTRAINT Manager CHECK ((TYPE_Manager = 1 AND TeamName IS NOT NULL) OR (TYPE_Manager = 0 AND TeamName IS NULL)),
    CONSTRAINT Engineer CHECK ((TYPE_Engineer = 1 AND Level IS NOT NULL AND Promote_Manager_EmployeeID IS NOT NULL) OR (TYPE_Engineer = 0 AND Level IS NULL AND Promote_Manager_EmployeeID IS NULL)),
    CONSTRAINT ProductManager CHECK ((TYPE_ProductManager = 1 AND Product IS NOT NULL) OR (TYPE_ProductManager = 0 AND Product IS NULL AND Interact_Customer_EmployeeID IS NULL))
);


CREATE TABLE Customer (
    CustomerID {ADD_TYPE} NOT NULL,
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
    NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.PlanWith_Manager_EmployeeID_A
        AND Employee.TYPE_Manager = 1
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of Manager!')

CREATE TRIGGER PlanWithManager
BEFORE INSERT ON PlanWith
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.PlanWith_Manager_EmployeeID_B
        AND Employee.TYPE_Manager = 1
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of Manager!')

CREATE TRIGGER PromoteManager
BEFORE INSERT ON Employee
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    N.TYPE_Engineer = 1 AND NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.Promote_Manager_EmployeeID
        AND Employee.TYPE_Manager = 1
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
        AND Employee.TYPE_Manager = 1
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of Manager!')