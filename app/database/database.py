import sqlite3
from app.schemas import ShipmentCreate,UpdateShipment
from typing import Any
from contextlib import contextmanager

class Database:
    def connect_to_db(self):
        print("connected to sqlite.db..")
        self.conn = sqlite3.connect("sqlite.db",check_same_thread=False)
        self.cur = self.conn.cursor()


    #create table if not exist
    def create_table(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS shipment (id INTEGER PRIMARY KEY, content TEXT, weight REAL, status TEXT)")

    
    def create(self,shipment:ShipmentCreate):
        self.cur.execute("SELECT MAX(id) FROM shipment")
        result = self.cur.fetchone()
        new_id = result[0] + 1 #result will be a tuple(12701,) so accessing first element
        self.cur.execute("INSERT INTO shipment VALUES(:id,:content,:weight,:status)",
                         {'id':new_id,'content':shipment.content,'weight':shipment.weight,'status':'new'}

                         )
        self.conn.commit()
        return new_id
    def get(self,id:int) -> dict[str,Any] | None:
        self.cur.execute("SELECT * FROM shipment WHERE id = ?",(id,))
        row = self.cur.fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "content": row[1],
            "weight": row[2],
            "status":row[3]

        }
    def update(self,id, shipment:UpdateShipment):
        self.cur.execute("UPDATE shipment SET status = :status WHERE id = :id",{"id":id,"status":shipment.status})
        self.conn.commit()
        return self.get(id)
    def delete(self,id:int):
        self.cur.execute("DELETE FROM shipment WHERE id = ?",(id,))
        self.conn.commit()
        

    def close(self):
        print("closing the connection..")
        self.conn.close()

     









# 1. Create a table


# 2. Add a row 
#cursor.execute("INSERT INTO shipment VALUES(12703, 'date treees', 22.7,'new')")
#connection.commit()

# 3. Read data 
#cursor.execute("SELECT status FROM shipment WHERE id = 12701")
#result = cursor.fetchall()
#print(result)

# 4. Update

#cursor.execute("UPDATE shipment SET status = 'placed' WHERE id = 12701")
#connection.commit()



# 5. Delete a shipment
#cursor.execute("DELETE FROM shipment WHERE id = 12703")
#connection.commit()




#close the connection when done
#connection.close()
