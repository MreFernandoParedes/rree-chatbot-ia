export interface ChatUserMessages {
    // userEmail: string | null;
    chatQuestion: string;
    chatAnswer: string;
    completionTokens: number;
    promptTokens: number;
    totalTokens: number;
}
