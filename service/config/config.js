/**
 * @author Đạt. Nguyễn Dương Minh Tâm
 * @email  nguyentamdat@gmail.com
 * @create date 22:17:38 09/03/2021
 * @modify date 14:50:42 18/03/2021
 * @desc Code Hard, Life Easy!
 */

module.exports = {
    port: process.env.PORT || 3000,
    workers: {
        shop: "http://localhost:3001/api/message"
    }
};