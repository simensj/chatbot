//onload(alert("hei"))

document.getElementById("chatbot_input_field").addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault(); // Prevents a new line in the textarea
        send_user_input();
    }
});

function send_user_input() {
    var user_input = document.getElementById("chatbot_input_field").value;
    if (user_input.trim() === "") return; // Prevent empty messages

    var chatDialog = document.getElementById("chat_dialog_field");
    if (!chatDialog) {
        chatDialog = document.createElement("div");
        chatDialog.id = "chat_dialog_field";
        document.body.prepend(chatDialog);
    }
    chatDialog.style.display = "flex";
    // Create the user message (right-aligned)
    var userMessageContainer = document.createElement("div");
    userMessageContainer.classList.add("chat_message_container", "user_message");

    var userMessageBubble = document.createElement("div");
    userMessageBubble.classList.add("chat_message", "user_bubble");
    userMessageBubble.textContent = user_input;

    userMessageContainer.appendChild(userMessageBubble);
    chatDialog.appendChild(userMessageContainer);

    // Create bot response (left-aligned)
    var botMessageContainer = document.createElement("div");
    botMessageContainer.classList.add("chat_message_container", "bot_message");

    var botMessageBubble = document.createElement("div");
    botMessageBubble.classList.add("chat_message", "bot_bubble");
    botMessageBubble.textContent = `OK, the user is asking me about "${user_input}"`;

    botMessageContainer.appendChild(botMessageBubble);
    chatDialog.appendChild(botMessageContainer);

    // Clear input field after sending message
    document.getElementById("chatbot_input_field").value = "";

    // Auto-scroll to the latest message
    chatDialog.scrollTop = chatDialog.scrollHeight;
}
