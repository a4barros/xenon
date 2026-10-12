import {genSalt} from "./random.js"
import { ITERATIONS, DERIVATION_FUNCTION, HASH_FUNCTION, AES_MODE, AES_LENGHT } from "./globals.js";
import {arrayBufferToBase64} from "./util.js"


async function generateAuthenticationKey(password) {
    const enc = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
        "raw",
        enc.encode(password),
        DERIVATION_FUNCTION,
        true,
        ["deriveBits"],
    );

    const salt = genSalt();
    const derivedBits = await window.crypto.subtle.deriveBits(
        {
            name: DERIVATION_FUNCTION,
            salt: salt,
            iterations: ITERATIONS,
            hash: HASH_FUNCTION,
        },
        keyMaterial,
        AES_LENGHT,
    );
    return {
        "authentication_key": arrayBufferToBase64(derivedBits),
        "salt": arrayBufferToBase64(salt),
    }
}

async function generateMasterKey() {
    return await window.crypto.subtle.generateKey(
        {
            name: AES_MODE,
            length: AES_LENGHT,
        },
        true,
        ["encrypt", "decrypt"],
    );
}





export { generateAuthenticationKey, generateMasterKey };