/**
 * @author Đạt. Nguyễn Dương Minh Tâm
 * @email  nguyentamdat@gmail.com
 * @create date 22:17:38 09/03/2021
 * @modify date 12:39:43 27/03/2021
 * @desc Code Hard, Life Easy!
 */

module.exports = {
    port: process.env.PORT || 3000,
    workers: {
        BanHangClassifier: "http://103.113.81.36:3000/botkit/receive"
    }
};