from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


inventory = {
    1: {
        "name": "Milk",
        "price": 100
    },

    2: {
        "name": "eggs",
        "price": 150
    }
}


@app.get("/")
def get_all_items():
    return inventory


@app.get("/get-item/{item_id}")
def get_specifc_item(item_id: int):
    return inventory[item_id]

@app.get("/get-by-name")
# # QUERY PARAMETER FUNCTION
def get_item_by_name(item_name: str):
    """
    Need to use '?' and paramter name with value to call this api.
    ex :  http://127.0.0.1:8000/get-by-name?item_name=Milk
    """
    for item_id in inventory:
        if inventory[item_id]["name"] == item_name:
            return  inventory[item_id]
    return {"Error" : "No Data with given item_name."}


@app.post("/create-item/{item_id}")
def create_item(item_id: int, item: Item):
    """ 
    Navigate to the /docs endpoint to pass the item.name, item.price
    Can't pass this data directly in the url, Alternatively we have to use 2 new params for name and price.
    """
    if item_id in inventory:
        return {"Error" : "Item_id already exist in the Inventory."}
    else:
        inventory[item_id] = item # (automatically will map all the keys, values)
        return inventory


@app.put("/update-item/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id in inventory:
        inventory[item_id] = item # (automatically will map all the keys, values)
    else: return {"Error" : "item_id does not exists in the Inventory."}


@app.delete("/delete-item/{item_id}")
def delete_item(item_id: int):
    if item_id in inventory:
        del inventory[item_id]
        return {"Success" : "Item deleted."}
    else:  return {"Error" : "item_id does not exists in the Inventory."}



## NOTE: Method1 to run the apis. 
# # uvicorn apis:app --reload

## NOTE: Method2 to run the apis.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500)




import requests

# GET All Items
response = requests.get("http://127.0.0.1:8000/")
print(response.json())

# POST Create Item
data = {"name": "Bread", "price": 50.0}
response = requests.post("http://127.0.0.1:8000/create-item/3", json=data)
print(response.json())

# DELETE Item
response = requests.delete("http://127.0.0.1:8000/delete-item/1")
print(response.json())


