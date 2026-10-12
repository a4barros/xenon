import { IV_LENGHT, SALT_LENGHT } from "./globals.js"

function genIv() {
    return window.crypto.getRandomValues(new Uint8Array(IV_LENGHT));
}

function genSalt() {
    return window.crypto.getRandomValues(new Uint8Array(SALT_LENGHT));
}

export {genIv, genSalt};