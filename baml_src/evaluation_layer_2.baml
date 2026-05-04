enum USER_INTENT {
  REPEAT_QUESTION
  REPHRASE_QUESTION
  PROVIDED_RESPONSE
}

class EvaluationLayerModel2 {
  user_intent USER_INTENT @description("Whether the user wants to repeat the question, rephrase the question, or has provided a response")
  rephrased_question string @description("The rephrased question. Include it only if user did not understand the question. Otherwise return an empty string")
}

function EvaluationLayer2(chat_history: string, current_question: string) -> EvaluationLayerModel2 {
  client OpenAIFast
  prompt #"
    {{ _.role("system") }}
    You are an evaluator. You are being shown chat history between an agent and a user. Agent has recently asked a question to the user. The same question is provided to you. You need to evaluate whether the user wants to repeat the question, rephrase the question, or has provided a response.
    
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

