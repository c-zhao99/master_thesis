CREATE TABLE Manager (
    EmployeeID {ADD_TYPE} NOT NULL,
    TeamName {ADD_TYPE} NOT NULL,
    Manage_Manager_EmployeeID {ADD_TYPE} UNIQUE NOT NULL REFERENCES Manager(EmployeeID),
    Manage_Engineer_EmployeeID {ADD_TYPE} UNIQUE NOT NULL REFERENCES Engineer(EmployeeID),
    PRIMARY KEY (EmployeeID),
    CONSTRAINT Manage CHECK ((Manage_Manager_EmployeeID IS NOT NULL AND Manage_Engineer_EmployeeID IS NULL) OR (Manage_Engineer_EmployeeID IS NOT NULL AND Manage_Manager_EmployeeID IS NULL))
);


CREATE TABLE Engineer (
    EmployeeID {ADD_TYPE} NOT NULL,
    Level {ADD_TYPE} NOT NULL,
    PRIMARY KEY (EmployeeID)
);


CREATE TABLE GovOfficial (
    GovID {ADD_TYPE} NOT NULL,
    Interact_Manager_Year {ADD_TYPE} NOT NULL,
    Interact_Engineer_Year {ADD_TYPE} NOT NULL,
    Interact_Manager_EmployeeID {ADD_TYPE} UNIQUE NOT NULL REFERENCES Manager(EmployeeID),
    Interact_Engineer_EmployeeID {ADD_TYPE} UNIQUE NOT NULL REFERENCES Engineer(EmployeeID),
    PRIMARY KEY (GovID),
    CONSTRAINT Interact CHECK ((Interact_Manager_EmployeeID IS NOT NULL AND Interact_Manager_Year IS NOT NULL AND Interact_Engineer_EmployeeID IS NULL AND Interact_Engineer_Year IS NULL) OR (Interact_Engineer_EmployeeID IS NOT NULL AND Interact_Engineer_Year IS NOT NULL AND Interact_Manager_EmployeeID IS NULL AND Interact_Manager_Year IS NULL))
);


CREATE TRIGGER Manager_Engineer
BEFORE INSERT ON Manager
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    EXISTS(
        SELECT *
        FROM Engineer
        WHERE N.EmployeeID = Engineer.EmployeeID
    )
)
SIGNAL SQLSTATE '70001' ('Only one child must exist with a specific identifier!')

CREATE TRIGGER Engineer_Manager
BEFORE INSERT ON Engineer
REFERENCING NEW AS N
FOR EACH ROW
WHEN (
    EXISTS(
        SELECT *
        FROM Manager
        WHERE N.EmployeeID = Manager.EmployeeID
    )
)
SIGNAL SQLSTATE '70001' ('Only one child must exist with a specific identifier!')