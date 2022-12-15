CREATE TABLE Users (
    UserID INT PRIMARY KEY NOT NULL,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    DateOfBirth DATE NOT NULL,
    ProfilePicture VARCHAR(200) NOT NULL,
    Bio VARCHAR(500) NOT NULL,
    Location VARCHAR(100) NOT NULL,
    Website VARCHAR(100)
);

INSERT INTO users (user_id, username, password, email, created_at, updated_at)
VALUES (1, 'johnsmith', 'password123', 'johnsmith@example.com', '2022-12-13 12:00:00', '2022-12-13 12:00:00');

INSERT INTO users (user_id, username, password, email, created_at, updated_at)
VALUES (2, 'janedoe', 'qwerty456', 'janedoe@example.com', '2022-12-13 12:00:00', '2022-12-13 12:00:00');

CREATE TABLE Tweets (
    tweet_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    body TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

INSERT INTO tweets (tweet_id, user_id, body, created_at, updated_at)
VALUES (1, 1, 'Hello, world!', '2022-12-13 12:00:00', '2022-12-13 12:00:00');

INSERT INTO tweets (tweet_id, user_id, body, created_at, updated_at)
VALUES (2, 1, 'Just had a great lunch.', '2022-12-13 12:00:00', '2022-12-13 12:00:00');

INSERT INTO tweets (tweet_id, user_id, body, created_at, updated_at)
VALUES (3, 2, 'I love Twitter!', '2022-12-13 12:00:00', '2022-12-13 12:00:00');

CREATE TABLE Likes (
    user_id INTEGER NOT NULL,
    tweet_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (tweet_id) REFERENCES Tweets(tweet_id),
    PRIMARY KEY (user_id, tweet_id)
);

