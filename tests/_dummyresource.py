from twisted.web.test.test_web import DummyRequest
from twisted.web import resource
from twisted.web import server
from teiler.client import FileRequestResource
from twisted.internet.defer import succeed, Deferred

class SmartDummyRequest(DummyRequest):
    def __init__(self, method, url, args=None, headers=None):
        DummyRequest.__init__(self, url.split('/'))
        self.method = method
        self.headers.update(headers or {})

        args = args or {}
        for k, v in args.items():
            self.addArg(k, v)

    def value(self):
        return "".join(self.written)


class DummySite(server.Site):
    def get(self, url, args=None, headers=None):
        return self._request("GET", url, args, headers)

    def post(self, url, args=None, headers=None):
        return self._request("POST", url, args, headers)

    def _request(self, method, url, args, headers):
        request = SmartDummyRequest(method, url, args, headers)
        resource = self.getResourceFor(request)
        result = resource.render(request)
        return self._resolveResult(request, result)

    def _resolveResult(self, request, result):
        if isinstance(result, str):
            request.write(result)
            request.finish()
            return succeed(request)
        elif result is server.NOT_DONE_YET:
            if request.finished:
                return succeed(request)
            else:
                return request.notifyFinish().addCallback(lambda _: request)
        else:
            raise ValueError("Unexpected return value: %r" % (result,))

class DummyRootResource(resource.Resource):
    """
    Creates a simple resource that can be used to construct a site.

    :param url: the url where the resource can be reached.
    :param resourceToTest: The resource to inject and test.
    """
    def __init__(self, url, resourceToTest):
        resource.Resource.__init__(self)
        self.putChild(url, resourceToTest) 
