import { ITERATIONS, DERIVATION_FUNCTION, HASH_FUNCTION, AES_MODE, AES_LENGHT } from "./globals.js";
import {base64ToArrayBuffer} from "./util.js"

async function unlockMasterKey(encryptedMasterKey, iv, salt, vaultPassword) {
    const enc = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
        "raw",
        enc.encode(vaultPassword),
        DERIVATION_FUNCTION,
        false,
        ["deriveKey"],
    );

    const wrappingKey = await window.crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: base64ToArrayBuffer(salt),
            iterations: ITERATIONS,
            hash: HASH_FUNCTION,
        },
        keyMaterial,
        { name: AES_MODE, length: AES_LENGHT },
        false,
        ["unwrapKey"],
    );

    return await window.crypto.subtle.unwrapKey(
        "raw",
        base64ToArrayBuffer(encryptedMasterKey),
        wrappingKey,
        {
            name: AES_MODE,
            iv: base64ToArrayBuffer(iv),
        },
        { name: AES_MODE, length: AES_LENGHT },
        true,
        ["encrypt", "decrypt"],
    );
}

async function unlockVault(encryptedVault, iv, masterKey) {
    const decryptedVault = await window.crypto.subtle.decrypt(
        { name: AES_MODE, iv: base64ToArrayBuffer(iv) },
        masterKey,
        base64ToArrayBuffer(encryptedVault),
    );
    return JSON.parse(new TextDecoder().decode(decryptedVault));
}

export { unlockMasterKey, unlockVault };
