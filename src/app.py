import argparse
from discover import client, server

# the main entry point for the application
# for simplicity, let's decide that the user decides at runtime to listen
# and the server decides to serve

def main():
    # get the arguments
    parser = argparse.ArgumentParser(description="Exchange files!")
    parser.add_argument("flag", metavar="F", type=int,
                        help="To be the server, use 1; to be the client, type any other number")
    args = parser.parse_args()
    app_runner(args.flag)

def app_runner(how):
    if how != 1:
        server.serve()
    else:
        client.listen()
    

if __name__  == '__main__':
    main()
