from convo_ticket import convert_conversation_to_ticket

def _file_reader(file_name: str):
  with open(file_name, 'r') as file:
    # Read the contents of the file into a string
    file_contents = file.read()
    return file_contents

def load_text(file_name: str):
  return _file_reader(file_name)

if __name__ == "__main__":
  print(convert_conversation_to_ticket(load_text('feature.txt')))