import { ChatUserMessages } from "./interfaces";
import storeChat from "./ChatStore";

const ChatManager = async ({ chatQuestion, chatAnswer, completionTokens, promptTokens, totalTokens }: ChatUserMessages) => {
    // TO DO: Agregar validación de email, además la pregunta y respuesta no deben ser strings vacíos.
    const response = await storeChat({ chatQuestion, chatAnswer, completionTokens, promptTokens, totalTokens });
    // console.log("response ChatManager:", response);
};

export default ChatManager;
