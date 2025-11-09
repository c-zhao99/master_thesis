CREATE TABLE Student (
    StudentID {ADD_TYPE} NOT NULL,
    PRIMARY KEY (StudentID)
);


CREATE TABLE Course (
    CourseID {ADD_TYPE} NOT NULL,
    PRIMARY KEY (CourseID)
);


CREATE TABLE Enroll (
    
    Enroll_Student_StudentID {ADD_TYPE} UNIQUE NOT NULL REFERENCES Student(StudentID),
    Enroll_Course_CourseID {ADD_TYPE} UNIQUE NOT NULL REFERENCES Course(CourseID),
    PRIMARY KEY (Enroll_Student_StudentID,Enroll_Course_CourseID)
);


