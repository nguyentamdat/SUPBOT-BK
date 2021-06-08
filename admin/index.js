const MongoClient = require('mongodb').MongoClient;
const uri = "mongodb+srv://admin:NhIUyo7mfafwErME@chatbot.y0fph.mongodb.net/myFirstDatabase?retryWrites=true&w=majority";
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });
client.connect(async (err) => {
    const collection = client.db("ConversationDatabase").collection("ConversationData");
    let cursor = collection.find({});
    await cursor.forEach(item => {
        console.log(item);
    });
    // perform actions on the collection object
    client.close();
});