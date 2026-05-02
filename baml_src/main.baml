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
