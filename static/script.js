function sendMessage() {

    let msg = document.getElementById("message").value;

    if(msg.trim() === ""){
        return;
    }

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "message=" + encodeURIComponent(msg)
    })

    .then(response => response.text())

    .then(data => {

        let box = document.getElementById("chatbox");

        box.innerHTML += `
            <div class="user">
                ${msg}
            </div>
        `;

        box.innerHTML += `
            <div class="bot">
                ${data}
            </div>
        `;

        document.getElementById("message").value = "";

        box.scrollTop = box.scrollHeight;
    });
}
document
.getElementById("message")
.addEventListener("keypress", function(event){

    if(event.key === "Enter"){
        sendMessage();
    }

});