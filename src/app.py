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
    parser.add_argument('directory',
                        help="The top level directory from which to serve files, e.g. '~/Downloads'",
                        )
    args = parser.parse_args()
    app_runner(args.action, args.directory)

def app_runner(how, where):
    if how == "serve":
        server.main(where)
    elif how == "listen":
        client.main()
    else:
        return u'Please specify either listen or serve'
    

if __name__  == '__main__':
    main()
