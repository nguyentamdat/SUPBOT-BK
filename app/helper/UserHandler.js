var mongo = require('mongodb').MongoClient;
var url = process.env.MONGO_URI;

module.exports = () => {
    let users = {};
    return {
        getUser: (id) => {
            return users[id];
        },
        newUser: (id) => {
            return users[id] = new User(id, {});
        }
    }
};

class User {
    constructor(id, state) {
        this.id = id;
        this.state = state;
        this.history = [];
        this.changes = [];
        this.votes = [];
        this.msg_id_counter = 0;
        var that = this;
        mongo.connect(url, (err, db) => {
            if (err) throw err;
            var dbo = db.db("ConversationDatabase");
            var obj = { user_id: that.id, history: that.history, changes: that.changes, votes: that.votes };
            dbo.collection("ConversationData").insertOne(obj, (err, res) => {
                if (err) throw err;
                db.close();
            });
        });
    }

    addMsg(msg) {
        this.history.push(msg);
        this.changes.push("");
        this.votes.push("");
        this.msg_id_counter++;
        this.save();
    }

    getNewMsg(msg) {
        this.addMsg(msg);
        return {
            msg_id: this.msg_id_counter - 1,
            text: msg,
            type: "message"
        }
    }

    changeMsg(msg_id, msg) {
        this.changes[msg_id] = msg;
        this.save();
    }

    vote(msg_id, v) {
        this.votes[msg_id] = v;
    }

    save() {
        var that = this;
        mongo.connect(url, (err, db) => {
            if (err) throw err;
            var dbo = db.db("ConversationDatabase");
            var obj = { $set: { user_id: that.id, history: that.history, changes: that.changes, votes: that.votes } };
            dbo.collection("ConversationData").updateOne({ user_id: that.id }, obj, (err, res) => {
                if (err) throw err;
                db.close();
            });
        });
    }
}