var user = document.forms['frmLogin']['usuario'];
var pwd = document.forms['frmLogin']['password'];

var user_error = document.getElementById('user_error');
var pass_error = document.getElementById('pass_error');

user.addEventListener('textInput', user_Verify);
pwd.addEventListener('textInput', pass_Verify);

function login() {
    if (user.value.length < 3) {
        user.style.border = "1px solid red";
        user_error.style.display = "block";
        user.focus();
        return false;
    }
    if (password.value.length < 3) {
        password.style.border = "1px solid red";
        pass_error.style.display = "block";
        password.focus();
        return false;
    }
}

function user_Verify() {
    if (user.value.length >= 3) {
        user.style.border = "1px solid silver";
        user_error.style.display = "none";;
        return true;
    }
}

function pass_Verify() {
    if (pwd.value.length >= 3) {
        pwd.style.border = "1px solid silver";
        pass_error.style.display = "none";;
        return true;
    }
}

function cerrarSesion() {
    var cerrar = document.getElementById("cerrar");
    location.href = "/login/";
}