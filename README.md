# livekit-practice

1. Text to Speech - uv run python .\text_to_speech.py console
2. Speech to Text - uv run python .\speech_to_text.py console
3. End of Turn - uv run python .\end_of_turn.py console
4. BAML replacing llm node - uv run python .\baml_llm_node.py console
5. Global state - uv run python .\global_state.py console
6. Store transcript - uv run python .\store_transcript.py console
7. Call tool - uv run python .\call_tool.py console
8. Question loop - uv run python .\question_loop.py console

## Commands

1.Install the cli 

`brew install livekit-cli`

2.Add project 
`lk cloud auth`


3.Add secrets in .env 

4.Deploy 
  `cd agent-gate && lk agent create`

5.Update a already deployed agent
  `lk agent deploy`

6.Run 
`uv run python .\conversation_flow.py console`

7.Dev server
`uv run python .\conversation_flow.py dev`

8. Realtime logs
`lk agent logs`

9. BAML client generate
`uv run baml-cli generate`
