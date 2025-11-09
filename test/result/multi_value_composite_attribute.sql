CREATE TABLE Person (
    SSN {ADD_TYPE} NOT NULL,
    BirthYear {ADD_TYPE} NOT NULL,
    PRIMARY KEY (SSN)
);


CREATE TABLE PersonWorkAddress (
    WorkAddress_ID {ADD_TYPE} NOT NULL,
    WorkAddress {ADD_TYPE} NOT NULL,
    Person_WorkAddress_Person_SSN {ADD_TYPE} UNIQUE NOT NULL REFERENCES Person(SSN),
    PRIMARY KEY (WorkAddress_ID)
);


