CREATE TABLE Customers (
    CustomerID SERIAL PRIMARY KEY NOT NULL,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Address VARCHAR(100) NOT NULL,
    PhoneNumber VARCHAR(15) NOT NULL,
    Email VARCHAR(100) NOT NULL
);

CREATE TABLE Accounts (
    AccountID INT PRIMARY KEY NOT NULL,
    AccountNumber VARCHAR(50) NOT NULL,
    CustomerID INT NOT NULL,
    AccountType VARCHAR(50) NOT NULL,
    Balance DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

CREATE TABLE Transactions (
    TransactionID INT PRIMARY KEY NOT NULL,
    AccountID INT NOT NULL,
    TransactionDate DATETIME NOT NULL,
    TransactionType VARCHAR(50) NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID)
);
