import argparse
from actions import server, client

# the main entry point for the application
# for simplicity, let's decide that the user decides at runtime to listen
# and the server decides to serve

def main():
    # get the arguments
    parser = argparse.ArgumentParser(description="Exchange files!")
    parser.add_argument('action',
                        help="To be the server, type serve; to be the client, type listen",
                        )
    args = parser.parse_args()
    app_runner(args.action)

def app_runner(how):
    if how == "serve":
        server.main()
    elif how == "listen":
        client.main()
    else:
        return u'Please specify either listen or serve'
    

if __name__  == '__main__':
    main()
