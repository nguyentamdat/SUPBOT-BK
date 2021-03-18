var rasa = require("../middlewares/middlewares")({
    rasa_uri: "http://localhost:5000",
});
const debug = require("debug")("botkit:domains");
const { BotkitConversation } = require("botkit");
const request = require("request-promise");
const TMT_ENDPOINT = "http://localhost:5001/api/send-message";

module.exports = function (controller) {
    controller.middleware.receive.use(rasa.receive);

    const onMessage = async (bot, message) => {
        debug("OnMessage", message);
        let { action, domain, intent } = message.nlu;
        if (action == "connect") {
            let options = {
                method: "POST",
                uri: "http://localhost:3002/connect",
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
                await bot.reply(message, "Đã kết nối và đợi tin nhắn từ worker");
            } else {
                await bot.reply(message, "Kết nối bị từ chối");
            }
        }
    };

    const onWelcomeBack = async (bot, message) => {
        debug("Welcome back");
        await bot.reply(message, "Chào mừng bạn");
    };

    const onImage = async (bot, message) => {
        let base64 = message.image;
        if (base64) {
            let options = {
                method: "POST",
                uri: `http://localhost:5000/image`,
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
                    await bot.reply(message, "Hình ảnh thuộc nhãn hàng khác");
                }
            });
        }
    };

    controller.on("welcome_back", onWelcomeBack);
    controller.on("hello", onWelcomeBack);
    controller.on("image", onImage);
    controller.on("message", onMessage);
};
