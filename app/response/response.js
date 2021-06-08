var response = {
  greet: ["xin chào bạn", "chào bạn", "hế nhô"],
  goodbye: ["tạm biệt nha", "hẹn gặp lại cậu lần sau nhé"],
  ask_name: ["mình tên là Ki"],
  ask_age: [
    "mình mới có 1 tuổi à",
    "tuổi tác không quan trọng",
    "hỏi tuổi tui chi chời",
  ],
  ask_love: [
    "bồ bịch gì tầm này, lo học hành đi",
    "đẹp trai thì mới có nhiều đứa yêu",
  ],
  ask_location: [
    "xa tận chân trời, gần ngay trước mắt",
    "mình ở trong chiếc máy tính xinh xinh của cậu nè",
  ],
  ask_gender: ["mình là con trai nhé, và mình cũng rất đẹp trai nữa"],
  ask_weather: [
    "nắng mưa là chuyện của trời, người phàm không biết được chính xác đâu",
  ]
}
module.exports = {
  get_response: (intent) => {
    if (response[intent])
      return response[intent][Math.floor(Math.random() * response[intent].length)];
    return null;
  }
};