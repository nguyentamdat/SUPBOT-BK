/**
 * @author Đạt. Nguyễn Dương Minh Tâm
 * @email  nguyentamdat@gmail.com
 * @create date 22:17:57 09/03/2021
 * @modify date 14:50:45 18/03/2021
 * @desc Code Hard, Life Easy!
 */

const express = require("express");
const app = express();
const Joi = require("joi");

const config = require("./config/config");

const port = process.env.PORT || 3000;

const CommonStateObject = Joi.object({
    user_id: Joi.string().required(),
    name: Joi.string(),
    age: Joi.number(),
    email: Joi.string().email(),
    phone: Joi.string().pattern(new RegExp("[0-9]{10,11}")),
    address: Joi.string(),
});

const ConnectObject = Joi.object({
    state: CommonStateObject.required(),
    domain: Joi.string().required(),
});

const DoneObject = Joi.object({
    state: CommonStateObject.required(),
});

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.get("/", (req, res) => {
    res.send("Hello world!");
});

app.get("/servers", (req, res) => {
    res.json(config.workers);
});

app.post("/connect", (req, res) => {
    const body = req.body;
    let { error, value } = ConnectObject.validate(body);
    let result = {
        worker_url: "",
        result: {},
    };
    if (error) {
        result.result = {
            code: -1,
            message: error
        };
        return res.json(result);
    }
    result.result = {
        code: 0,
        message: "accepted"
    };
    return res.json(result);
});

app.post("/done", (req, res) => {
    const body = req.body;
    let { error, value } = DoneObject.validate(body);
    let result = {
        result: "",
    };
    if (error) {
        result.result = error.message;
        return res.json(result);
    }
    result.result = "accept";
    return res.json(result);
});

app.listen(port, () => {
    console.log(`Listening at http://localhost:${port}`);
});
