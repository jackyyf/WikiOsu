#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: Yifu Yu <root@jackyyf.com>

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from tornado.httpserver import HTTPServer
from tornado.httpclient import AsyncHTTPClient
from tornado.gen import coroutine, Return
from tornado.netutil import bind_sockets, bind_unix_socket
from tornado.process import fork_processes
from json import loads, dumps
from urllib import urlencode
from sys import exc_info

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

with open('key.txt', 'r') as f:
	api_key = f.read().strip()

api_base = 'https://osu.ppy.sh/api'
listen_addr = 'unix:/dev/shm/osuapi-v1.sock'

class UserHandler(RequestHandler):
	@coroutine
	def get(self, user):
		client = AsyncHTTPClient()
		upstream_url = api_base + '/get_user?' + urlencode({
			'k': api_key,
			'u': user,
		})
		resp = yield client.fetch(upstream_url, validate_cert=False)
		if resp.code != 200:
			self.set_status(resp.code)
			self.write(resp.body)
			self.finish()
		else:
			# Query succeed.
			data = resp.body
			try:
				data_list = loads(data)
			except ValueError as e:
				self.set_status(500)
				self.write(e.message)
				self.finish()
				raise Return
			if not data_list:
				self.set_status(404)
				self.write('Not Found')
				self.finish()
				raise Return
			try:
				user_obj = data_list[0]
				self.write(dumps(user_obj))
				self.finish()
			except:
				self.write(exc_info()[0])
				self.finish()

class MapHandler(RequestHandler):
	@coroutine
	def get(self, map_id):
		client = AsyncHTTPClient()
		upstream_url = api_base + '/get_beatmaps?' + urlencode({
			'k': api_key,
			'b': map_id,
		})
		resp = yield client.fetch(upstream_url, validate_cert=False)
		if resp.code != 200:
			self.set_status(resp.code)
			self.write(resp.body)
			self.finish()
		else:
			# Query succeed.
			data = resp.body
			try:
				data_list = loads(data)
			except ValueError as e:
				self.set_status(500)
				self.write(e.message)
				self.finish()
				raise Return
			if not data_list:
				self.set_status(404)
				self.write('Not Found')
				self.finish()
				raise Return
			try:
				map_obj = data_list[0]
				self.write(dumps(map_obj))
				self.finish()
			except:
				self.write(exc_info()[0])
				self.finish()

def run_server():
	app = Application([
		url(r'/user/(.+)', UserHandler),
		url(r'/map/(.+)', MapHandler),
	])
        if listen_addr.startswith('unix:'):
            socket = [bind_unix_socket(listen_addr[5:], mode=0660)]
        else:
            if ':' in listen_addr:
                addr, port = listen_addr.rsplit(':', 1)
                port = int(port)
            else:
                addr = None
                port = int(listen_addr)
            socket = bind_sockets(port, addr)
        fork_processes(0)
        server = HTTPServer(app)
        server.add_sockets(socket)
	IOLoop.instance().start()

if __name__ == '__main__':
	run_server()
