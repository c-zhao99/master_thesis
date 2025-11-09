CREATE TABLE Person (
    SSN {ADD_TYPE} NOT NULL,
    PRIMARY KEY (SSN)
);


CREATE TABLE Car (
    ChassisNumber {ADD_TYPE} NOT NULL,
    Owns_Person_SSN {ADD_TYPE} UNIQUE NOT NULL REFERENCES Person(SSN),
    PRIMARY KEY (ChassisNumber)
);


