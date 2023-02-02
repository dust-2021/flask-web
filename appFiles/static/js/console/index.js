/* jshint esversion: 6 */
const web_console = '/web_console';

function logout() {
    "use strict";
    let xhr = new XMLHttpRequest();
    // xhr.onreadystatechange = function () {
    //     if (xhr.readyState === 4){
    //         if (xhr.readyState === 302){
    //             window.location.href = xhr.responseURL;
    //             console.log(xhr.responseURL);
    //         }
    //     }
    // };
    xhr.onload = function () {
        window.location.href = web_console + "/login";
    };
    xhr.open("GET", web_console + "/logout", true);
    xhr.send(null);
}

function login(simple_login = false) {

    if (simple_login === true){
        let xhr = new XMLHttpRequest();
        xhr.open('get',web_console + '/simple_login', false);
        xhr.onload = function (){
            if(xhr.status === 200 && xhr.readyState === 4){
                console.log(xhr.responseURL);
                window.location.href = xhr.responseURL;
            }
        };
        xhr.send();
        return
    }

    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    let remember = document.getElementById('remember').value;

    let xhr = new XMLHttpRequest();
    let data = new FormData();

    let dom = document.getElementById('tips');

    if (username === "" || password === "") {
        dom.style.color = "red";
        dom.innerText = '用户名和密码不能为空';
        return null;
    }

    data.append("username", username);
    data.append("password", password);
    data.append("remember", remember);
    xhr.onload = function () {
        let resp = JSON.parse(xhr.responseText);
        if (resp.message) {
            window.location.href = web_console + '/';
        } else {
            dom.innerText = '用户名或密码错误';
            dom.style.color = 'red';
        }
    };
    xhr.open("POST", web_console + '/login', false);
    xhr.send(data);
}

function register() {
    "use strict";
    let username = document.getElementById('username').value;
    if (username === null || username === '') {
        username = document.getElementById('username').getAttribute('placeholder');
    }
    let password = document.getElementById('password').value;
    let password_check = document.getElementById('password_check').value;
    let ele = document.getElementById('checker');

    if (password.length <= 6) {
        ele.hidden = false;
        ele.innerText = "密码至少为6位";
        ele.style.color = 'red';
        return;
    }

    if (password !== password_check) {
        ele.hidden = false;
        ele.innerText = "密码不一致";
        ele.style.color = 'red';
        return;
    }

    let xhr = new XMLHttpRequest();

    xhr.open('POST', web_console + "/account/register", true);
    let data = new FormData();
    data.append("username", username);
    data.append("password", password);


    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                let reData = JSON.parse(xhr.responseText);
                if (reData.success === true) {
                    ele.innerText = '注册成功';
                    ele.hidden = false;
                    let log = document.createElement("a");
                    let dom = document.getElementById("regForm");
                    log.setAttribute("class", "btn btn-primary");
                    log.setAttribute("href", web_console + "/login");
                    log.setAttribute("float", "right");
                    log.innerText = "返回登录";
                    dom.appendChild(log);
                } else {
                    ele.innerText = reData.message;
                    ele.style.color = 'red';
                    ele.hidden = false;
                }
            }
        }
    };
    xhr.send(data);
}
