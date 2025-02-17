document.getElementById("chatbot_input_field").addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault(); // Prevents a new line in the textarea
        send_user_input();
        toggle_input(false)
    }
});
function toggle_input(isActive){
if (isActive == true){
    document.getElementById("chatbutton").removeAttribute("disabled")
    document.getElementById("chatbot_input_field").removeAttribute("disabled")
} 
else {
    document.getElementById("chatbutton").setAttribute("disabled", "")
    document.getElementById("chatbot_input_field").setAttribute("disabled", "")
}
}

function send_user_input() {
    var user_input = document.getElementById("chatbot_input_field").value.trim();
    if (user_input === "") return; // Prevent empty messages
    
    var chatDialog = get_chat_dialog();

    // Create the user message
    create_message(user_input, "user");
    create_message("fetching response...", "bot");
    // Send a request to the chatbot and fetch its response
    (async () => {
        try {
            const response = await fetch("https://jsonplaceholder.typicode.com/posts/1", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();
            console.log(data);
            create_message(`Response successful: ${JSON.stringify(data.body)}`, "bot");

        } catch (error) {
            console.error(error);
            create_message(`Error: ${error.message}`, "bot");
        }
        toggle_input(true)
        // Clear input field after sending message
        document.getElementById("chatbot_input_field").value = "";
        chatDialog.scrollTop = chatDialog.scrollHeight; // Auto-scroll to the latest message
    })();
}

function get_chat_dialog() {
    var chatDialog = document.getElementById("chat_dialog_field");
    if (!chatDialog) {
        chatDialog = document.createElement("div");
        chatDialog.id = "chat_dialog_field";
        document.body.prepend(chatDialog);
    }
    chatDialog.style.display = "flex";
    return chatDialog;
}

function create_message(text, sender) {
    var chatDialog = get_chat_dialog();
    
    var messageContainer = document.createElement("div");
    messageContainer.classList.add("chat_message_container", sender === "user" ? "user_message" : "bot_message");

    var messageBubble = document.createElement("div");
    messageBubble.classList.add("chat_message", sender === "user" ? "user_bubble" : "bot_bubble");
    messageBubble.textContent = text;

    messageContainer.appendChild(messageBubble);
    chatDialog.appendChild(messageContainer);
}
