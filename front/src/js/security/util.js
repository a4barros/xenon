function byteArrayToBase64(byteArray) {
    let binaryString = '';
    const chunkSize = 0x8000; // 32KB chunks
    for (let i = 0; i < byteArray.length; i += chunkSize) {
        const chunk = byteArray.subarray(i, i + chunkSize);
        binaryString += String.fromCharCode.apply(null, chunk);
    }
    return btoa(binaryString);
}

function base64ToByteArray(base64String) {
    const binaryString = atob(base64String);
    const byteArray = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        byteArray[i] = binaryString.charCodeAt(i);
    }
    return byteArray;
}

function arrayBufferToBase64(arrayBuffer) {
    const byteArray = new Uint8Array(arrayBuffer);
    return byteArrayToBase64(byteArray);
}

function base64ToArrayBuffer(base64String) {
    const byteArray = base64ToByteArray(base64String);
    return byteArray.buffer;
}

export { arrayBufferToBase64, base64ToArrayBuffer };