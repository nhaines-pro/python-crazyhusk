# Standard Library
import glob
import sqlite3
from contextlib import closing


def main():
    for coverage_db in glob.iglob("./.coverage.*"):
        with closing(sqlite3.connect(coverage_db)) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute("UPDATE file SET path=REPLACE(path,'\\','/')")
                connection.commit()


if __name__ == "__main__":
    main()
