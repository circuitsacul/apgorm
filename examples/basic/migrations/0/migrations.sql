CREATE TABLE _migrations ();
CREATE TABLE users ();
ALTER TABLE _migrations ADD COLUMN id_ INTEGER;
ALTER TABLE users ADD COLUMN nickname VARCHAR(32);
ALTER TABLE users ADD COLUMN username VARCHAR(32);
ALTER TABLE _migrations ALTER COLUMN id_ SET NOT NULL;
ALTER TABLE users ALTER COLUMN username SET NOT NULL;
ALTER TABLE _migrations ADD CONSTRAINT _migrations_id__primary_key PRIMARY KEY ( id_ );
ALTER TABLE users ADD CONSTRAINT users_username_primary_key PRIMARY KEY ( username );