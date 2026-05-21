\c postgres;
DROP DATABASE IF EXISTS books; 
CREATE DATABASE books;
\c books;

CREATE TABLE Books 
(
    BookID SERIAL PRIMARY KEY, 
    ISBN VARCHAR(16) UNIQUE NOT NULL,
    Title VARCHAR(256) NOT NULL, 
    Author VARCHAR(64) NOT NULL, 
    Year INT NOT NULL,
    Created TIMESTAMP NOT NULL, 
    Modified TIMESTAMP 
);

CREATE TABLE Users 
(
    UserID SERIAL PRIMARY KEY,
    Username VARCHAR(32) UNIQUE NOT NULL, 
    Password VARCHAR(1024) NOT NULL,
    Created TIMESTAMP NOT NULL, 
    Modified TIMESTAMP
);

CREATE TABLE Reviews
(   
    ReviewID SERIAL PRIMARY KEY, 
    PostedBy INT NOT NULL,
    ReviewOf INT NOT NULL,
    Review VARCHAR(512) NOT NULL,
    Score INT NOT NULL,
    Created TIMESTAMP NOT NULL, 
    Modified TIMESTAMP,

    CONSTRAINT fk_postedBy
      FOREIGN KEY(PostedBy) 
	  REFERENCES Users(UserID),

    CONSTRAINT fk_reviewOf
      FOREIGN KEY(ReviewOf) 
	  REFERENCES Books(BookID)
);