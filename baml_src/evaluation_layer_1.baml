enum ON_TOPIC_STATUS_1 {
  ON_TOPIC @description("User's answer is related to the question we asked.")
  OFF_TOPIC @description("User's answer is not related to the question we asked.")
}

class EvaluationLayerModel1 {
  on_topic_status ON_TOPIC_STATUS_1 @description("Whether the user's answer is on topic or not")
}

function EvaluationLayer1(chat_history: string, current_question: string) -> EvaluationLayerModel1 {
  client OpenAIFast
  prompt #"
    {{ _.role("system") }}
    You are an evaluator. You are being shown chat history between an agent and a user. Agent has recently asked a question to the user. The same question is provided to you. You need to evaluate whether the user's response is on topic or off topic.
    
    This is a transcript from speech so do not flag punctuation errors.

    {{ _.role("user") }}
    Conversation History:
    ---
    {{ chat_history }}
    ---

    This is the current question that we are tracking
    {{ current_question }}

    {{ctx.output_format }}
  "#
}

