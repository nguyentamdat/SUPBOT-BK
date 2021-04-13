var rasa = require("../middlewares/middlewares")({
  rasa_uri: `${process.env.AI_URL}`,
});
const debug = require("debug")("botkit:domains");
const { BotkitConversation } = require("botkit");
const request = require("request-promise");

var UserState = [];

module.exports = function (controller) {
  controller.middleware.receive.use(rasa.receive);

  const onMessage = async (bot, message) => {
    debug("OnMessage", message);
    let { action, domain, intent, isQuestion } = message.nlu;
    if (isQuestion) {
      let options = {
        uri: `${process.env.AI_URL}/ask`,
        json: {
          question: message.text,
        },
        method: "post",
      };
      let res = await request(options);
      return await bot.reply(message, res.body[1]);
    }
    if (
      bot._config.domain !== undefined &&
      bot._config.domain == "BanHangClassifier"
    ) {
      let reply = await request({
        method: "post",
        body: { text: message.text, type: "message" },
        json: true,
        uri: message._config.domain.url,
      });
      console.log(reply);
      return await bot.reply(message, reply.text);
    }
    if (action == "connect") {
      let options = {
        method: "POST",
        uri: `${process.env.SERVICE_URL}`,
        body: {
          state: {
            user_id: message.user,
          },
          domain: domain,
        },
        json: true,
      };
      let res = await request(options);
      if (res.result.code == 0) {
        let reply = await request({
          method: "post",
          body: { text: message.text, type: "message" },
          json: true,
          uri: res.result.url,
        });
        bot._config.domain = {
          url: res.result.url,
          domain: domain,
        };
        console.log(reply);
        await bot.reply(message, reply.text);
      } else {
        await bot.reply(message, JSON.stringify(res.result));
      }
      return;
    }
    if (action == "default") {
      return await bot.reply(message, "Bạn đã nhắn: " + message.text);
    }
  };

  const onWelcomeBack = async (bot, message) => {
    debug("Welcome back");
    await bot.reply(message, "Chào mừng bạn");
  };

  const onImage = async (bot, message) => {
    debug("onImage");
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
        let isFashion = response.body.action;
        if (isFashion) {
          await bot.reply(message, "Đây là hình thời trang");
        } else {
          await bot.reply(
            message,
            "Xin lỗi bạn, hiện tại hệ thống chưa hỗ trợ sản phẩm này."
          );
        }
      });
    }
  };

  let typing = new BotkitConversation("typing", controller);

  typing.say("I am going to type for a while now...");
  typing.addAction("typing");

  // start the typing indicator
  typing.addMessage({ type: "typing" }, "typing");
  // trigger a gotoThread, which gives us an opportunity to delay the next message
  typing.addAction("next_thread", "typing");

  typing.addMessage("typed!", "next_thread");

  // use the before handler to delay the next message
  typing.before("next_thread", async () => {
    return new Promise((resolve) => {
      // simulate some long running process
      setTimeout(resolve, 3000);
    });
  });

  controller.addDialog(typing);

  controller.on("welcome_back", onWelcomeBack);
  controller.on("hello", onWelcomeBack);
  controller.on("image", onImage);
  controller.on("message", onMessage);
};
