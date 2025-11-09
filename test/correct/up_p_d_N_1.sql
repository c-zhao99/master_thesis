CREATE TABLE Employee (
    EmployeeID {ADD_TYPE} NOT NULL,
    TeamName {ADD_TYPE},
    Level {ADD_TYPE},
    Product {ADD_TYPE},
    PlanWith_Manager_Year {ADD_TYPE},
    TYPE_ManagerEngineerProductManager VARCHAR(50) NOT NULL CHECK (TYPE_ManagerEngineerProductManager IN (['Manager', 'Engineer', 'ProductManager', 'Employee'])),
    PlanWith_Manager_EmployeeID {ADD_TYPE} UNIQUE REFERENCES Employee(EmployeeID),
    Promote_Manager_EmployeeID {ADD_TYPE} UNIQUE REFERENCES Employee(EmployeeID),
    Manage_Manager_EmployeeID {ADD_TYPE} UNIQUE REFERENCES Employee(EmployeeID),
    Interract_Customer_CustomerID {ADD_TYPE} UNIQUE REFERENCES Customer(CustomerID),
    PRIMARY KEY (EmployeeID),
    CONSTRAINT ManagerEngineerProductManager CHECK ((TYPE_ManagerEngineerProductManager = Manager AND TeamName IS NOT NULL AND Level IS NULL AND Product IS NULL AND Promote_Manager_EmployeeID IS NULL AND Interract_Customer_EmployeeID IS NULL) OR (TYPE_ManagerEngineerProductManager = Engineer AND Level IS NOT NULL AND PlanWith_Manager_EmployeeID IS NULL AND PlanWith_Manager_Year IS NULL AND TeamName IS NULL AND Product IS NULL AND Promote_Manager_EmployeeID IS NOT NULL AND Interract_Customer_EmployeeID IS NULL) OR (TYPE_ManagerEngineerProductManager = ProductManager AND Product IS NOT NULL AND PlanWith_Manager_EmployeeID IS NULL AND PlanWith_Manager_Year IS NULL AND TeamName IS NULL AND Level IS NULL AND Promote_Manager_EmployeeID IS NULL) OR (TYPE_ManagerEngineerProductManager = Employee AND TeamName IS NULL AND Level IS NULL AND Product IS NULL AND PlanWith_Manager_EmployeeID IS NULL AND PlanWith_Manager_Year IS NULL AND Promote_Manager_EmployeeID IS NULL AND Interract_Customer_EmployeeID IS NULL))
);


CREATE TABLE Customer (
    CustomerID {ADD_TYPE} NOT NULL,
    PRIMARY KEY (CustomerID)
);


CREATE TRIGGER PlanWithManager
BEFORE INSERT ON Employee
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    N.TYPE_ManagerEngineerProductManager = Manager AND NOT EXISTS(
        SELECT * FROM Employee
        WHERE Employee.EmployeeID = N.PlanWith_Manager_EmployeeID
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