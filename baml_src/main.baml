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
    You are a helpful and conversational assistant.

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
