# Distributed_Systems
A Note Taking app the handles consistency.


for this you need to have docker install and running so that you can excecute the following command: 

    docker run -d -p 27017:27017 --name mongodb mongo:7

## New python server instructions to test MongoDB connection

From you repository root, run:

```
docker compose up --build
```
This builds the FastAPI server, starts MongoDB in a separate container, 
connects both services inside Docker network and exposes the server at http://localhost:8000
Once the containers are running, open:

```
http://localhost:8000/test-db
```
If you see JSON output like this:
```
{
  "status": "Connected to MongoDB",
  "inserted_id": "<some-id>",
  "notes": [
    { "title": "Test Note", "content": "This is a test note." }
  ]
}
```
The connection is working