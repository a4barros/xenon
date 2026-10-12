import {generateAuthenticationKey, generateMasterKey} from "./security/key.js"
import {protectMasterKey, protectVault} from "./security/encryption.js"


const BASE_URL = "http://localhost:8000"

document.getElementById("createAccount").addEventListener("click", async function (event) {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const vaultPassword = document.getElementById("vaultPassword").value;

    const authenticationKey = await generateAuthenticationKey(password);
    const masterKey = await generateMasterKey();
    const protectedMasterKey = await protectMasterKey(masterKey, vaultPassword);
    const vault = createVault();
    const protectedVault = await protectVault(vault, masterKey);


    await sendProtectedPayloadToServer(username, authenticationKey, protectedMasterKey, protectedVault);
});

async function sendProtectedPayloadToServer(username, authenticationKey, protectedMasterKey, protectedVault) {
    const payload = {
        "username": username,
        "authentication_key": authenticationKey.authentication_key,
        "salt": authenticationKey.salt,
        "protected_master_key": protectedMasterKey,
        "protected_vault": protectedVault
    }
    await fetch(`${BASE_URL}/user/`, {
        "content-type": "application/json",
        "body": JSON.stringify(payload),
        "method": "POST",
    });
}

function createVault() {
    return {
        "version": "1",
        "contents": [
            {
                "name": "example",
                "username": "user",
                "password": "123",
                "totpKey": null,
                "notes": "",
                "createdOn": "2020-01-01",
                "updatedOn": "2020-01-01",
                "trashedOn": null
            }
        ]
    }
}