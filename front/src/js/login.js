import {generateAuthenticationKeyForLogin} from "./security/keyDer.js"
import {BASE_URL} from "./security/baseUrl.js"

document.getElementById("login").addEventListener("click", async function (event) {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const vaultPassword = document.getElementById("vaultPassword").value;
    const salt = await getUserSalt(username)

    const key = await generateAuthenticationKeyForLogin(password, salt)

    login(username, key)
    const masterKey = getMasterKey()
    decryptMasterKey(vaultPassword, masterKey.salt, masterKey.iv)
    decryptVault()


    window.location.href = "index.html";
});

async function getUserSalt(username) {
    const response = await fetch(`${BASE_URL}/user/${username}/salt`, {
        "credentials": "include",
        "headers": {
            "Content-Type": "application/json"
        },
        "method": "GET",
        "mode": "cors"
    });

    if (response.status === 200) {
        const data = await response.json();
        return data.salt;
    } else {
        throw new Error(`Failed to get user salt: ${response.status}`);
    }
}

async function getMasterKey() {
    const response = await fetch(`${BASE_URL}/master/`, {
    "credentials": "include",
    "headers": {
        "Authorization": localStorage.getItem("token"),
    },
    });

    return await response.json()
}

async function login(username, key) {
    const response = await fetch(`${BASE_URL}/user/token`, {
        "credentials": "include",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        "body": `grant_type=password&username=${username}&password=${key}`,
        "method": "POST",
        "mode": "cors"
    });
    if (response.status !== 200) {
        alert("Login failed. Please check your username and password.");
        return;
    }

    const j = await response.json();
    const token = `${j.token_type} ${j.access_token}`;
    localStorage.setItem("token", token);
}