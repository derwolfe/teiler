from twisted.web.client import getPage

# XXX belongs on client
def submitFileRequest(recipient, postdata, headers):
    """
    Post the file request information to another user.
    """
    log.msg("submitFileRequest:: data:", recipient, system="httpFileTransfer")
    return getPage(recipient,
                   method='POST',
                   postdata=postdata,
                   headers=headers)
