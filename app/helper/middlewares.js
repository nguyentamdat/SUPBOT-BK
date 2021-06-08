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
    receive: async (bot, message, next) => {
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
          uri: `${config.rasa_uri}/chat`,
          body: {
            text: message.text,
            id: message.user,
          },
          json: true,
        };

        options2 = {
          method: "POST",
          uri: `${process.env.RASA_URL}/model/parse`,
          body: {
            text: message.text,
          },
          json: true,
        };
      }

      let res = await request(options);
      message.nlu = res;

      if (options2) {
        let res = await request(options2);
        message.intent = res.intent.name;
      }

      next();
    },

    hears: (patterns, domain) => {
      debug("Patterns", patterns);
      return async (message) => {
        if (message.domain.toLowerCase() !== domain.toLowerCase()) {
          return false;
        }
        return patterns.some((pattern) => {
          if (message.intent.toLowerCase() === pattern.toLowerCase()) {
            debug("Rasa intent matched hear pattern", message.intent, pattern);
            return true;
          }
        });
      };
    },
  };
  return middleware;
};
