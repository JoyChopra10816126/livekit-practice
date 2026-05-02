generator target {
  output_type "python/pydantic"
  output_dir "../"
  version "0.222.0"
}

class Response {
  grammatical_errors_present bool @description("True if there are any grammatical errors in the transcript")
  corrected_transcript string @description("The corrected transcript of the user's speech")
  explanation_for_student string @description("The explanation for the student in a conversational tone")
}

function GetResponse(chat_history: string) -> Response {
  client OpenAIFast
  prompt #"
    {{ _.role("system") }}
    You are a helpful and conversational assistant. This is a transcript from speech
    so do not flag punctuation errors.

    EXAMPLE:
    {
      "grammatical_errors_present": true,
      "corrected_transcript": "I went to the store.",
      "explanation_for_student": "Have a great day!"
    }

    {{ _.role("user") }}
    Conversation History:
    ---
    {{ chat_history }}
    ---

    Respond now following the Response schema.
  "#
}

class Response2 {
  acknowledgement string @description("Say a small acknowledgement for the users input")
  is_answer_satisfactory bool @description("Say whether the answer is correct or not")
  evidence_for_satisfaction string @description("Provide evidence that user answer is satisfactory")
  probe_question string @description("Provide a question for the user if answer is not satisfactory to probe them further. Only make this field non-empty if the answer is not satisfactory.")
}

function GetResponse2(chat_history: string) -> Response2 {
  client OpenAIFast
  prompt #"
    {{ _.role("system") }}
    You are a helpful and conversational assistant. This is a transcript from speech
    so do not flag punctuation errors.

    {{ _.role("user") }}
    Conversation History:
    ---
    {{ chat_history }}
    ---

    {{ctx.output_format }}

    Respond now following the Response schema.
  "#
}

enum DiagnosticGoalMetStatus { 
  YES
  NO
}

class ExtractedField {
  field_name string @description("The name of the field")
  field_value string @description("The value of the field")
}

class Response3 {
  is_diagnostic_goal_met DiagnosticGoalMetStatus @description("True if the user's answer meets the diagnostic goal for the current question")
  extracted_fields ExtractedField[] @description("Array of all fields that need to be extracted from the user's answer. If a field is not found, put a null value for it and add it to the list")
  diagnostic_gap string @description("If diagnostic goal is not met, identify what is missing?")
  probe_question string @description("Based on the diagnostic gap, create a new question that needs to be asked to user.")
  
}



function GetResponse3(chat_history: string, diagnostic_goal: string, expected_fields: string[], current_question: int) -> Response3 {
  client OpenAIFast
  prompt #"
    {{ _.role("system") }}
    You are a helpful and conversational assistant. This is a transcript from speech
    so do not flag punctuation errors.

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

    Respond now following the Response schema.
  "#
}

enum ON_TOPIC_STATUS {
  ON_TOPIC @description("User's answer is related to the question we asked.")
  OFF_TOPIC @description("User's answer is not related to the question we asked.")
}

enum TURN_DECISION {
  REPEAT_QUESTION @description("Repeat the same question")
  PARAPHRASE_QUESTION @description("Rephrase the same question")
  ANALYSE_RESPONSE @description("Analyse the response")
}

class Response4 {
  on_topic_status ON_TOPIC_STATUS @description("Whether the user's answer is on topic or not")
  turn_decision TURN_DECISION @description("Whether to repeat the question, rephrase the question, or analyse the response")
  rephrased_question string @description("Rephrased version of the question based on user request")
}

function GetResponse4(chat_history: string, current_question: int) -> Response4 {
  client OpenAIFast
  prompt #"
    {{ _.role("system") }}
    You are a helpful and conversational assistant. This is a transcript from speech
    so do not flag punctuation errors.

    {{ _.role("user") }}
    Conversation History:
    ---
    {{ chat_history }}
    ---

    This is the current question that we are tracking
    {{ current_question }}

    Analyse if the user wants to repeat question, paraphrase it or has given a response

    {{ctx.output_format }}

    Respond now following the Response schema.
  "#
}