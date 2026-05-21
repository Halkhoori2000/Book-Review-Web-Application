# Used to import the data in books.csv to the database 
import psycopg2
import csv 

def load():
    # Connect 
    with psycopg2.connect(
        database='books', user='postgres', 
        password='246432', host='localhost', port='5432' # pls place password here and save 246432
    ) as conn:
        # Open cursor 
        cursor = conn.cursor()

        # Truncate books table 
        cursor.execute('TRUNCATE books CASCADE;')

        # Read the csv file 
        with open("db/books.csv") as books_file:
            csvreader = csv.reader(books_file)

            # Skip header
            next(csvreader)

            count = 0;

            for row in csvreader:
                # Escape single quotes 
                r = [item.replace("'", "''") for item in row]

                # Insert
                sql = f"INSERT INTO books (ISBN, Title, Author, Year, Created) VALUES ('{r[0]}', '{r[1]}', '{r[2]}', '{r[3]}', NOW());"
                cursor.execute(sql)

                count += 1

        conn.commit()

        print(f"{count} books inserted")

if __name__ == '__main__':
    load() 