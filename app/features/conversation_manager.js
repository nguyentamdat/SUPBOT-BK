var rasa = require("../middlewares/middlewares")({
  rasa_uri: `${process.env.AI_URL}`,
});
const debug = require("debug")("botkit:domains");
const { BotkitConversation } = require("botkit");
const request = require("request-promise");

var UserState = {};

const _THREAD_HOLD = 0.1;

defaultUserState = (ref) => ({
  subscriber: [],
  ref: ref,
});

function createUserState(m) {
  for (let u in UserState) {
    if (m.user === u) {
      return UserState[u];
    }
  }
  return defaultUserState(m.reference);
}

function getUserState(m) {
  for (let u in UserState) {
    if (m === u) {
      return UserState[u];
    }
  }
  return null;
}

function isOnline(user) {
  for (let u in UserState) {
    if (u === user) {
      return true;
    }
  }
  return false;
}

module.exports = function (controller) {
  controller.middleware.receive.use(rasa.receive);

  controller.middleware.ingest.use(async (bot, message, next) => {
    let userState = createUserState(message);
    for (let subscriber of userState.subscriber) {
      let notifyBot = await controller.spawn();
      await notifyBot.changeContext(subscriber);
      await notifyBot.say(`User ${subscriber.user.id} said: ` + message.text);
    }
    next();
  });

  controller.interrupts("subscribe", "message", async (bot, message) => {
    let userState = createUserState(message);
    let subscribe = message.text.split(" ")[1];
    if (subscribe != null) {
      let subscribeState = getUserState(subscribe);
      subscribeState.subscriber.push(userState.ref);
    }
    return await bot.reply(
      message,
      "Bạn đã lắng nghe người dùng: " + subscribe
    );
  });

  controller.interrupts("list", "message", async (bot, message) => {
    let user = message.user;
    let reply = [];
    console.log(UserState);
    for (let u in UserState) {
      if (u !== user) {
        reply.push({
          title: u,
          payload: `subscribe ${u}`,
        });
      }
    }
    await bot.reply(message, {
      text: "Server hiện có các user sau",
      quick_replies: reply,
    });
  });

  const onMessage = async (bot, message) => {
    debug("[onMessage]", message);
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
      return await bot.reply(message, res[1]);
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
      // console.log(reply);
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
        return await bot.reply(message, reply.text);
      }
      return await bot.reply(message, JSON.stringify(res.result));
    }
    if (action == "default") {
      let options = {
        method: "POST",
        uri: `${process.env.GPT_URL}/generate`,
        body: {
          text: message.text
        },
        json: true,
      };
      let res = await request(options);
      return await bot.reply(message, res.text);
    }
  };

  const onWelcomeBack = async (bot, message) => {
    debug("Welcome back");
    UserState[message.user] = await createUserState(message);
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

  controller.on("welcome_back", onWelcomeBack);
  controller.on("hello", onWelcomeBack);
  controller.on("image", onImage);
  controller.on("message", onMessage);
};
