const request = require("request-promise");
const debug = require("debug")("botkit:middleware-rasa");

module.exports = (config) => {
    if (!config) {
        config = {};
    }

    if (!config.uri) {
        config.uri = "http://localhost:5005"
    }

    var middleware = {
        receive: async (bot, message, next) => {
            if (!message.text) {
                next();
                return;
            }

            let options = {
                method: "POST",
                uri: `${process.env.RASA_URL}/model/parse`,
                body: {
                    text: message.text,
                },
                json: true,
            }

            let res = await request(options);
            message.intent = res.intent.name;
            next();
        }
    };

    return middleware;
}