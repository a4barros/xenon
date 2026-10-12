import {genIv, genSalt} from "./random.js"
import { ITERATIONS, DERIVATION_FUNCTION, HASH_FUNCTION, AES_MODE, AES_LENGHT } from "./globals.js";
import {arrayBufferToBase64} from "./util.js"

async function protectMasterKey(masterKey, vaultPassword) {
    const enc = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
        "raw",
        enc.encode(vaultPassword),
        DERIVATION_FUNCTION,
        false,
        ["deriveKey"],
    );

    const salt = genSalt();

    const wrappingKey = await window.crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: ITERATIONS,
            hash: HASH_FUNCTION,
        },
        keyMaterial,
        { name: AES_MODE, length: AES_LENGHT },
        true,
        ["wrapKey", "unwrapKey"],
    );

    const iv = genIv();

    const encryptedMasterKey = await window.crypto.subtle.wrapKey("raw", masterKey, wrappingKey, {
        name: AES_MODE,
        iv,
    });

    return {
        "encrypted_master_key": arrayBufferToBase64(encryptedMasterKey),
        "salt": arrayBufferToBase64(salt),
        "iv": arrayBufferToBase64(iv)
    } 
}

async function protectVault(vault, masterKey) {
    const iv = genIv();
    const enc = new TextEncoder();
    const encryptedVault = await window.crypto.subtle.encrypt(
        { name: AES_MODE, iv },
        masterKey, 
        enc.encode(JSON.stringify(vault)));
    return {
        "iv": arrayBufferToBase64(iv),
        "encrypted_vault": arrayBufferToBase64(encryptedVault)
    }
}

export { protectMasterKey, protectVault };