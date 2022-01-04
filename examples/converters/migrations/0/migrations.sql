CREATE TABLE _migrations ();
CREATE TABLE players ();
ALTER TABLE _migrations ADD COLUMN id_ INTEGER;
ALTER TABLE players ADD COLUMN status INTEGER;
ALTER TABLE players ADD COLUMN username VARCHAR(32);
ALTER TABLE _migrations ALTER COLUMN id_ SET NOT NULL;
ALTER TABLE players ALTER COLUMN username SET NOT NULL;
ALTER TABLE _migrations ADD CONSTRAINT _migrations_id__primary_key PRIMARY KEY ( id_ );
ALTER TABLE players ADD CONSTRAINT players_username_primary_key PRIMARY KEY ( username );