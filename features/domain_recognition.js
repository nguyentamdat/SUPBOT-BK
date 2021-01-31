var rasa = require("../middlewares/middlewares")({
    rasa_uri: "http://localhost:5000",
});
const debug = require("debug")("botkit:domains")

module.exports = function (controller) {
    controller.middleware.receive.use(rasa.receive);

    controller.hears(
        ["nha khoa"],
        "message",
        async (bot, message) => {
            debug("Received", message.incoming_message);
            await bot.reply(message, "Chào bạn, bạn muốn tư vấn gì về nha khoa?");
        }
    );

    controller.hears(
        ["thời trang", "quần áo"],
        "message",
        async (bot, message) => {
            debug("Received", message.incoming_message);
            await bot.reply(message, "Chào bạn, bạn muốn tư vấn gì về thời trang?");
        }
    );
};
