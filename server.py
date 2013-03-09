#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import functools

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

import Queue
import time

queue = Queue.Queue()
jobs = {}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world!")
        

class PushHandler(tornado.web.RequestHandler):
    def get(self, job_id, job_result):
        #self.write(job_id + job_result)
        job = jobs[job_id]        
        self.write("push ok")
        callback = job['callback']
        #callback(job_result)
        tornado.ioloop.IOLoop.instance().add_callback(functools.partial(callback, job_result))
        del jobs[job_id]        
        
class PullHandler(tornado.web.RequestHandler):
    #def get(self):
    #    job = queue.get(block=True)
    #    job_id = job['job_id']
    #    method = job['method']
    #    jobs[job_id] = job        
    #    
    #    self.write(dict(job_id=job_id, method=method))
    #
    @tornado.web.asynchronous
    def get(self):
        self.pull_job()
 
    def pull_job(self):
        try:
            job = queue.get_nowait()
            job_id = job['job_id']
            method = job['method']
            jobs[job_id] = job
            self.write(dict(job_id=job_id, method=method))
            self.finish()
        except Queue.Empty:            
            tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 0.1, self.pull_job)

 
class RpcHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, method):
        #self.write("Hello, world, %s" % method)
        job = {'job_id':'123456', 'method':method, 'callback':self.on_response}
        queue.put(job)

    def on_response(self, data):
        self.finish(data)

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/push/(.{6})/(.*)", PushHandler),
        (r"/pull/", PullHandler),
        (r"/rpc/(.*)", RpcHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
