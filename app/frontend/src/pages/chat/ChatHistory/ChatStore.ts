import { ChatUserMessages } from "./interfaces";

const storeChat = async (ChatData: ChatUserMessages): Promise<{ success: boolean; message: string }> => {
    try {
        const response = await fetch(`/storechat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(ChatData)
        });
        if (response.ok) {
            const responseData = await response.json();
            // console.log("response data:", responseData);
            return { success: true, message: responseData };
        } else {
            const errorMessage = await response.text();
            console.log("response error:", errorMessage);
            return { success: false, message: errorMessage };
        }
    } catch (error) {
        console.error("Error logging in:", error);
        return { success: false, message: "An error occurred while registering chats." };
    }
};

export default storeChat;
