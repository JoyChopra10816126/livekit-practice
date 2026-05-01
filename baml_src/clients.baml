client<llm> OpenAIFast {
  provider openai
  retry_policy Exponential
  options {
    model "gpt-4.1-nano"
    api_key env.OPENAI_API_KEY
  }
}

retry_policy Exponential {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 2000
    multiplier 2.0
    max_delay_ms 30000
  }
}
