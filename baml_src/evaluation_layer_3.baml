enum DiagnosticGoalMetStatus1 { 
  YES
  NO
}

class ExtractedField1 {
  field_name string @description("The name of the field")
  field_value string @description("The value of the field")
}

class EvaluationLayerModel3 {
  is_diagnostic_goal_met DiagnosticGoalMetStatus1 @description("True if the user's answer meets the diagnostic goal for the current question")
  extracted_fields ExtractedField1[] @description("Array of all fields that need to be extracted from the user's answer. If a field is not found, put a null value for it and add it to the list")
  diagnostic_gap string @description("If diagnostic goal is not met, identify what is missing?")
  probe_question string @description("Based on the diagnostic gap, create a new question that needs to be asked to user.")
  acknowledgement string @description("Acknowledgement for the user. Generate it to acknowledge user's response")
}

function EvaluationLayer3(chat_history: string, diagnostic_goal: string, expected_fields: string[], current_question: string) -> EvaluationLayerModel3 {
  client OpenAIFast
  prompt #"
    {{ _.role("system") }}
    You are an evaluator. You are being shown chat history between an agent and a user. Agent has recently asked a question to the user. The same question is provided to you. You need to evaluate whether the user's response meets the diagnostic goal for current question. If it does not meet, then you need to identify the gap and ask a probe question to the user to fill that gap.
    
    This is a transcript from speech so do not flag punctuation errors.

    {{ _.role("user") }}
    Conversation History:
    ---
    {{ chat_history }}
    ---

    This is the current question that we are tracking
    {{ current_question }}

    Make sure the user's answer meets the following diagnostic goal for current question
    {{ diagnostic_goal }}

    Extract following fields from the user's answer
    {{ expected_fields }}

    {{ctx.output_format }}
  "#
}