const request = require("request-promise");
const debug = require("debug")("botkit:middleware");

module.exports = (config) => {
    if (!config) {
        config = {};
    }

    if (!config.rasa_uri) {
        config.rasa_uri = "http://localhost:5000";
    }

    var middleware = {
        receive: (bot, message, next) => {
            if ((!message.text && !message.image) || message.is_echo) {
                next();
                return;
            }

            let options;
            if (message.image) {
                options = {
                    method: "POST",
                    uri: `${config.rasa_uri}/image`,
                    body: {
                        id: message.user,
                        base64: message.image,
                    },
                    json: true,
                };
            }

            if (message.text) {
                options = {
                    method: "POST",
                    uri: `${config.rasa_uri}/domain`,
                    body: {
                        text: message.text,
                        id: message.user,
                    },
                    json: true,
                };
            }

            request(options).then((response) => {
                debug("Rasa response", response);
                message.nlu = response.body;
                next();
            });
        },

        hears: (patterns, domain) => {
            debug("Patterns", patterns);
            return async (message) => {
                if (
                    message.body.domain.toLowerCase() !== domain.toLowerCase()
                ) {
                    return false;
                }
                return patterns.some((pattern) => {
                    if (
                        message.body.intent.toLowerCase() ===
                        pattern.toLowerCase()
                    ) {
                        debug(
                            "Rasa intent matched hear pattern",
                            message.body.intent,
                            pattern
                        );
                        return true;
                    }
                });
            };
        },
    };
    return middleware;
};