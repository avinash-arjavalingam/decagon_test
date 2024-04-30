import json
from openai_helper import query_conversation, OutputTypes
from linear import run_linear_graphql_query, run_linear_graphql_mutation


API_KEY = '<INSERT VALUE HERE>'
OPEN_AI_KEY =  '<INSERT VALUE HERE>'

def convert_conversation_to_ticket(user_text: str):
  classification_prompt = f"""
  Determine if the content between three backticks is a feature request, a bug report, or neither
  ```{user_text}```
  provide the output only in a JSON format where the key is "type", and the value is an integer, either 0 for feature request, 1 for bug request, and 2 for neither.
  """

  ticket_type = None
  class_response = query_conversation(classification_prompt, OPEN_AI_KEY)
  response_type = class_response['type']
  if response_type == OutputTypes.FEATURE.value:
    ticket_type = 'feature request'
  elif response_type == OutputTypes.BUG.value:
    ticket_type = 'bug report'
  else:
      output_type_strs = [str(output_type) for output_type in list(OutputTypes)]
      return f"Conversation was not one of: {output_type_strs}"

  if ticket_type:
    issues_info = f"""
    {{
      issues {{
        nodes {{
          id
          title
          description
        }}
      }}
    }}
    """

    issues_present = json.dumps(run_linear_graphql_query(issues_info, API_KEY)['data']['issues']['nodes'])

    issues_overlap_prompt = f"""
    Between the three backticks is a json blob containing the information of the current tickets
    ```{issues_present} ```.
    Between the next three pluses is the current text that we are considering
    +++{user_text}+++.
    Determine if the information in the current text is has already generally been recorded in any of the current tickets.
    Provide the output only in a JSON format where the key is "provided", and the value is either 0 for False (the information is novel) or 1 for True (one or more of the tickets already contains the information of the current text)
    """

    overlap_response = query_conversation(issues_overlap_prompt, OPEN_AI_KEY)
    provided = bool(overlap_response['provided'])
    if provided:
      return "Did not create a new ticket, as it was determined the information is already present in the current backlog"

    summary_prompt = f"""
    For the purposes of making a JIRA-like ticket, write a title and a summary of the text between the three backticks
    ```{user_text} ```
    provide the output only in a JSON format, with one key value pair with a key of "title", and the value being the title you wrote, and the other pair having key "summary", and the value being the summary you wrote.
    You don't need to include "feature request" or "bug report" in the title or summary, it is implied
    """
    response = query_conversation(summary_prompt, OPEN_AI_KEY)

    teams_info = """
    {
      teams {
        nodes {
          id
          name
        }
      }
    }
    """

    teams_id = run_linear_graphql_query(teams_info, API_KEY)['data']['teams']['nodes'][0]['id']

    label_info = """
    {
      issueLabels {
        nodes {
          id
          name
        }
      }
    }
    """

    label_types = run_linear_graphql_query(label_info, API_KEY)['data']['issueLabels']['nodes']
    label_id = None
    if response_type == OutputTypes.FEATURE.value:
      label_id = json.dumps([label_type['id'] for label_type in label_types if label_type['name'] == str(OutputTypes.FEATURE)])
    elif response_type == OutputTypes.BUG.value:
      label_id = json.dumps([label_type['id'] for label_type in label_types if label_type['name'] == str(OutputTypes.BUG)])


    user_text = json.dumps(f"{response['summary']} \n\n\n Full text: \n\n\n {user_text}")

    ticket_info = f"""
    {{
      issueCreate(
        input: {{
          title: "{response['title']}"
          description: {user_text}
          teamId: "{teams_id}"
          labelIds: {label_id}
        }}
      ) {{
      success
        issue {{
          id
          title
        }}
      }}
    }}
    """

    ticket_response = run_linear_graphql_mutation(ticket_info, API_KEY)
    return ticket_response