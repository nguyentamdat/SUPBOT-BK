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
      if (!message.text || message.is_echo) {
        next();
        return;
      }

      debug("Sending message to Rasa", message.text);
      const options = {
        method: "POST",
        uri: `${config.rasa_uri}/whichbot`,
        body: {
          text: message.text,
        },
        json: true,
      };

      request(options).then((response) => {
        debug("Rasa response", response);
        message.intent = response.intent;
        next();
      });
    },

    hears: (patterns, message) => {
      debug("Patterns", patterns);
      debug("message", message);
      return patterns.some((pattern) => {
        if (message.intent.name === pattern) {
          debug("Rasa intent matched hear pattern", message.intent, pattern);
          return true;
        }
      });
    },
  };
  return middleware;
};
