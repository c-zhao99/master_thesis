CREATE TABLE Employee (
    EmployeeID {ADD_TYPE} NOT NULL,
    TeamName {ADD_TYPE},
    Level {ADD_TYPE},
    Product {ADD_TYPE},
    TYPE_Manager VARCHAR(50) NOT NULL CHECK (TYPE_Manager IN (['0', '1'])),
    TYPE_Engineer VARCHAR(50) NOT NULL CHECK (TYPE_Engineer IN (['0', '1'])),
    TYPE_ProductManager VARCHAR(50) NOT NULL CHECK (TYPE_ProductManager IN (['0', '1'])),
    Promote_Engineer_EmployeeID {ADD_TYPE} UNIQUE REFERENCES Employee(EmployeeID),
    Manage_Employee_EmployeeID {ADD_TYPE} UNIQUE REFERENCES Employee(EmployeeID),
    PRIMARY KEY (EmployeeID),
    CONSTRAINT TOTAL_HIERARCHY CHECK ((TYPE_Manager=1 OR TYPE_Engineer=1 OR TYPE_ProductManager=1)),
    CONSTRAINT Manager CHECK ((TYPE_Manager = 1 AND TeamName IS NOT NULL AND Promote_Engineer_EmployeeID IS NOT NULL AND Manage_Employee_EmployeeID IS NOT NULL) OR (TYPE_Manager = 0 AND TeamName IS NULL AND Promote_Engineer_EmployeeID IS NULL AND Manage_Employee_EmployeeID IS NULL)),
    CONSTRAINT Engineer CHECK ((TYPE_Engineer = 1 AND Level IS NOT NULL) OR (TYPE_Engineer = 0 AND Level IS NULL)),
    CONSTRAINT ProductManager CHECK ((TYPE_ProductManager = 1 AND Product IS NOT NULL) OR (TYPE_ProductManager = 0 AND Product IS NULL))
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


CREATE TABLE Interact (
    
    Interact_ProductManager_EmployeeID {ADD_TYPE} UNIQUE NOT NULL REFERENCES Employee(EmployeeID),
    Interact_Customer_CustomerID {ADD_TYPE} UNIQUE NOT NULL REFERENCES Customer(CustomerID),
    PRIMARY KEY (Interact_ProductManager_EmployeeID,Interact_Customer_CustomerID)
);


CREATE TRIGGER PlanWithManager
BEFORE INSERT ON PlanWith
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    N.TYPE_Manager = 1 AND NOT EXISTS(
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
    N.TYPE_Manager = 1 AND NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.PlanWith_Manager_EmployeeID_B
        AND Employee.TYPE_Manager = 1
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of Manager!')

CREATE TRIGGER PromoteEngineer
BEFORE INSERT ON Employee
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    N.TYPE_Manager = 1 AND NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.Promote_Engineer_EmployeeID
        AND Employee.TYPE_Engineer = 1
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of Engineer!')

CREATE TRIGGER InteractProductManager
BEFORE INSERT ON Interact
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.Interact_ProductManager_EmployeeID
        AND Employee.TYPE_ProductManager = 1
    )
)
SIGNAL SQLSTATE '70001' ('Inserted tuple needs to reference an instance of ProductManager!')