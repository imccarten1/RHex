from gtpinterface2 import GTPInterface2

def main():
  """
  Main function, simply sends user input on to the gtp interface and prints
  responses.
  """
  
  interface = GTPInterface2("dca")
  while True:
    command = input()
    success, response = interface.send_command(command)
    print(("= " if success else "? ")+response+'\n')

if __name__ == "__main__":
  main()
