
import urllib2
import time
import simplejson

def now():
    print time.strftime("%Y%m%d%H%m%S")
    #return time.ctime()
    return time.strftime("%Y%m%d%H%m%S")

def pull():
    print "pull"
    data = urllib2.urlopen("http://127.0.0.1:8888/pull/").read()
    job = simplejson.loads(data)
    return job

def push(job):
    print "push"
    url = "http://127.0.0.1:8888/push/%s/%s" % (job['job_id'], job['result'])
    data = urllib2.urlopen(url).read()
    print data

def execute(job):
    method = job['method']
    call = globals()[method]
    result = call()
    job['result'] = result
    return job

def _run():
    job = pull()
    job = execute(job)
    push(job)
    
def run_forever():
    while True:
        _run()
    
def main():
    run_forever()

if __name__ == '__main__':
    main()