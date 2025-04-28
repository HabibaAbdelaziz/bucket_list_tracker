import uvicorn
from fastapi import FastAPI
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database Configs
SQL_DB_URL = "sqlite:///./test.db" # telling my app where the db is.
engine = create_engine(SQL_DB_URL) # creating an engine that knows how to connect to my db
"""
Using sessionmaker, I'm creating sessions (connections) to talk to my db.
autocommit=False means that I must tell it to save my changes manually (safer).
It is safer to not do autocommit bec it gives me the chance to:
1) Double-check changes
2) Catch errors BEFORE they mess up the db
3) Cancel bad changes if sth goes wrong (by calling session.rollback())
We use 'session.commit()' to save our changes to the db.
'autoflush=False' is used so we don't automattically send changes to the db unless I say so.
'bind=engine' means we are using the engine we just built to connect to the db.
"""
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# We created a base class that all the database models (tables) will inherit from.
Base=declarative_base()


# SQLAlchemy models
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index= True)
    name = Column(String, index=True)
    description = Column(String, index=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

#########################
# CRUD operations

#### Create
@app.post("/items/")
async def create_item(name: str, description: str):
    db = SessionLocal()
    try:
        db_item = Item(name=name, description=description)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    finally:
        db.close()

### Read (GET)
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.id==item_id).first()
        return item
    finally:
        db.close()

### Update (PUT)
@app.put("/items/{item_id}")
async def update_item(item_id: int, name: str, description: str):
    db = SessionLocal()
    try:
        db_item = db.query(Item).filter(Item.id==item_id).first()
        db_item.name=name
        db_item.description=description
        db.commit()
        return db_item
    finally:
        db.close()

### Delete (DELETE)
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    db = SessionLocal()
    try:
        db_item = db.query(Item).filter(Item.id==item_id).first()
        db.delete(db_item)
        db.commit()
        return {"message": "Item deleted successfully"}
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run(app)