import { MongoClient } from "mongodb";

async function main() {
  const uri = "mongodb://localhost:27017"; // local MongoDB
  const client = new MongoClient(uri);

  try {
    await client.connect();
    console.log("Connected to MongoDB!");

    const db = client.db("mydatabase"); // create/use database
    const collection = db.collection("users"); // create/use collection

    // Example: insert a document
    const result = await collection.insertOne({ name: "Chris", age: 25 });
    console.log("Inserted document with _id:", result.insertedId);

    // Example: read documents
    const users = await collection.find().toArray();
    console.log("All users:", users);

  } finally {
    await client.close();
  }
}

main().catch(console.error);


