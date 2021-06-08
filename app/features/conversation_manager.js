var rasa = require("../helper/middlewares")({
  rasa_uri: `${process.env.AI_URL}`,
});
const debug = require("debug")("botkit:domains");
const { BotkitConversation } = require("botkit");
const request = require("request-promise");
const { get_response } = require("../response/response");
const users = require("../helper/UserHandler")();

const _THREAD_HOLD = 0.05;

module.exports = function (controller) {
  controller.middleware.receive.use(rasa.receive);

  controller.middleware.send.use(async (bot, message, next) => {
    let options = {
      uri: `${process.env.AI_URL}/bot`,
      json: {
        text: message.text,
        id: message.conversation.id,
      },
      method: "post",
    };
    let result = await request(options);
    next();
  });

  const onMessage = async (bot, message) => {
    debug("[onMessage]", message.text);
    let user = users.getUser(message.user);
    user.addMsg(message.text);
    let { action, domain, intent, isQuestion, history } = message.nlu;

    // handle question first
    if (isQuestion) {
      let options = {
        uri: `${process.env.AI_URL}/ask`,
        json: {
          question: message.text,
        },
        method: "post",
      };
      let res = await request(options);
      let reply = user.getNewMsg(res[1]);
      return await bot.reply(message, reply);
    }

    // // handle chat with client
    // if (
    //   bot._config.domain !== undefined &&
    //   bot._config.domain == "BanHangClassifier"
    // ) {
    //   let reply = await request({
    //     method: "post",
    //     body: { text: message.text, type: "message" },
    //     json: true,
    //     uri: message._config.domain.url,
    //   });
    //   return await bot.reply(message, reply.text);
    // }

    // handle normal chat
    if (get_response(message.intent)) {
      let reply = get_response(message.intent);
      reply = user.getNewMsg(reply);
      return await bot.reply(message, reply);
    }

    // // handle connect to client
    // if (action == "connect") {
    //   let options = {
    //     method: "POST",
    //     uri: `${process.env.SERVICE_URL}`,
    //     body: {
    //       state: {
    //         user_id: message.user,
    //       },
    //       domain: domain,
    //     },
    //     json: true,
    //   };
    //   let res = await request(options);
    //   if (res.result.code == 0) {
    //     let reply = await request({
    //       method: "post",
    //       body: { text: message.text, type: "message" },
    //       json: true,
    //       uri: res.result.url,
    //     });
    //     bot._config.domain = {
    //       url: res.result.url,
    //       domain: domain,
    //     };
    //     return await bot.reply(message, reply.text);
    //   }
    //   return await bot.reply(message, JSON.stringify(res.result));
    // }

    // handle auto generate chat from gpt server
    if (action == "default") {
      let options = {
        method: "POST",
        uri: `${process.env.GPT_URL}/generate`,
        body: {
          text: history,
        },
        json: true,
      };
      let res = await request(options);
      let reply = res.text === "" ? "Tôi không thể hiểu bạn!" : res.text;
      reply = user.getNewMsg(reply);
      return await bot.reply(
        message,
        reply
      );
    }
  };

  const onWelcomeBack = async (bot, message) => {
    debug("[onWelcomeBack]");
    if (users.getUser(message.user) == null) {
      await onHello(bot, message);
    }
  };
  const onHello = async (bot, message) => {
    debug("[onHello]");
    let user = users.newUser(message.user);
    let msg = get_response("greet");
    msg = user.getNewMsg(msg);
    await bot.reply(message, msg);
  };

  const onDisconnect = async (bot, message) => {
    debug("[onDisconnect]");
  };

  const onImage = async (bot, message) => {
    debug("[onImage]");
    let base64 = message.image;
    if (base64) {
      let options = {
        method: "POST",
        uri: `${process.env.AI_URL}/image`,
        body: {
          id: message.user,
          base64: message.image,
        },
        json: true,
      };

      await request(options).then(async (response) => {
        debug("Rasa response", response);
        let isFashion = response.action;
        if (isFashion > _THREAD_HOLD) {
          await bot.reply(message, {
            text: "Bạn có muốn nhận hỗ trợ về sản phẩm này không?",
            quick_replies: [
              {
                title: "Yes",
                payload: "Yes",
              },
              { title: "No", payload: "No" },
            ],
          });
        } else {
          await bot.reply(
            message,
            "Xin lỗi bạn, hiện tại hệ thống chưa hỗ trợ sản phẩm này."
          );
        }
      });
    }
  };

  const onChangeMsg = (bot, message) => {
    let user = users.getUser(message.user);
    user.changeMsg(message.msg_id, message.new_msg);
    debug("[onChangeMsg]", user);
  };

  const onVote = (bot, message) => {
    let user = users.getUser(message.user);
    debug("[onVote]", user);
    user.vote(message.msg_id, message.vote);
  }

  controller.on("welcome_back", onWelcomeBack);
  controller.on("hello", onHello);
  controller.on("image", onImage);
  controller.on("message", onMessage);
  controller.on("change", onChangeMsg);
  controller.on("disconnect", onDisconnect);
  controller.on("vote", onVote);
};
