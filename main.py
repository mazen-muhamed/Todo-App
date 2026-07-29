from fastapi import FastAPI

app = FastAPI()

todos = []

@app.get("/")
def home():
    return {"message": "Todo API is running"}
@app.get("/todos")
def get_todos():
    return todos
@app.post("/todos/add")
def add_todo(text: str):
    todo = {
        "id": len(todos) + 1,
        "task_name": text,
        "status": False
    }

    todos.append(todo)

    return {
        "message": "Task added successfully",
        "todo": todo
    }
@app.post("/todos/{id}/toggle")
def toggle_todo(id: int):

    for todo in todos:
        if todo["id"] == id:
            todo["status"] = not todo["status"]
            return todo

    return {"message": "Task not found"}
@app.post("/todos/{id}/update")
def update_todo(id: int, text: str):

    for todo in todos:
        if todo["id"] == id:
            todo["task_name"] = text
            return todo

    return {"message": "Task not found"}
@app.delete("/todos/{id}")
def delete_todo(id: int):

    for todo in todos:
        if todo["id"] == id:
            todos.remove(todo)
            return {"message": "Task deleted"}

    return {"message": "Task not found"}