var response = {
    greet: ["xin chào bạn, hôm nay bạn có gì vui không?", "chào bạn, ngày hôm nay tuyệt nhỉ", "hế nhô, bạn ổn chứ?"],
    goodbye: ["tạm biệt nha", "bye bye"],
    ask_name: ["tui tên là KiBot, còn bạn tên gì?"],
    ask_age: [
        "mình mới có 1 tuổi à",
        "tuổi tác không quan trọng",
        "hỏi tuổi tui chi chời",
    ],
    ask_love: [
        "bồ bịch gì tầm này",
        "đẹp thì mới có nhiều đứa yêu",
    ],
    ask_location: [
        "xa tận chân trời, gần ngay trước mắt",
        "tui ở ngay trước mắt nè",
    ],
    ask_gender: ["mình là con trai nhé, và mình cũng rất đẹp trai nữa"],
    ask_weather: [
        "nắng mưa là chuyện của trời, tui làm sao biết được",
    ]
}
module.exports = {
    get_response: (intent) => {
        if (response[intent])
            return response[intent][Math.floor(Math.random() * response[intent].length)];
        return null;
    }
};