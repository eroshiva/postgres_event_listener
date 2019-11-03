# Postgres Python Listener

## Usage
Before launching program please follow these steps to setup & prepare Postgres DB.
Mainly inspired by this [article](https://blog.lelonek.me/listen-and-notify-postgresql-commands-in-elixir-187c49597851)

#### Create Postgres DB with some dummy values

Loggin in Postgres DB with following command:
```bash
sudo -u postgres psql
```

Creating a testing DB:
```sql
CREATE DATABASE test_db;
```

Creating a specific user which will manage this DB:
```sql
CREATE USER test_user PASSWORD 'password123';
```
We created a user “test_user” with password “password123”

Grant all privileges to this user with new database (it will help to retrieve all info from the db):
```sql
GRANT ALL PRIVILEGES ON TABLE test_table TO test_user;
```
Connecting to the newly created database with following command:
```sql
\c test_db
```
Inspect which tables are created within this database:
```sql
\dt
```
Create a new table in a database:
```sql
CREATE TABLE test_table ( id integer, status text, band text, song text, logged_at text );
```
In this table we will store songs of different bands and their status (released or upcoming), like on a music recording label

Filling newly created table with some values:
```sql
INSERT INTO test_table VALUES (1, 'Released', 'RHCP', 'Wet Sand', ‘-’);
INSERT INTO test_table VALUES (2, 'Released', 'RHCP', 'My Lovely Man', ‘-’);
INSERT INTO test_table VALUES (3, 'Released', 'Rufus Du Sol', 'Underwater', ‘-’);
INSERT INTO test_table VALUES (4, 'Upcoming', 'Josh Klinghoffer', 'Pluralone', ‘-’);
```
To check, if there is actually something in table, use following command:
```sql
\dt+
```
If the output is non-zero, your information was inserted.

To insert modifications, use following command:
```sql
UPDATE test_table SET status = ‘Released’ WHERE song = ‘Pluralone’;
```
It will update status of the song *“Pluralone”* (it's actually upcoming album :P).

#### Trigger notifications on Postgres DB

To create a notifications with publish/subscribe mechanism, first you should add a client listener on certain channel (like topic). 
All subscribers listening to the channel will be notified asynchronously (NOTIFY command with that topic would be executed).
Payload with changed data can be passed to indicate what has been changed.

Create a function first by inserting following lines (insert Enter after each line):
```sql
CREATE FUNCTION notify_changes() RETURNS trigger AS $$
BEGIN
PERFORM pg_notify(
'accounts_changed', /* Channel name */
json_build_object( /* Payload */
'operation', TG_OP,
'record', row_to_json(NEW)
)::text
);
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```
After that you should see *“CREATE FUNCTION”* message dropped to the Cli. It means that the function was created.

Once we did this, we should create trigger for notification to be sent (same steps as for function 	creation):
```sql
CREATE TRIGGER info_changed
AFTER INSERT OR UPDATE
ON test_table /* name of the table to publish changes */
FOR EACH ROW
EXECUTE PROCEDURE notify_changes();
```

Now the Postgres DB is set. 
It will send notifications to the channel *"accounts_changed"* each time you insert or update any filed in the DB.
