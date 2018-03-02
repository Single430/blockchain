#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
 * Created by zbl on 18-3-2 上午10:05.
"""

import json

import logger
import traceback
from uuid import uuid4

import tornado.options
from tornado import web, wsgi, ioloop
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

from blockchain import BlockChain

LOGGER = logger.Logger()
block_chain = BlockChain()
node_identifier = str(uuid4()).replace('-', '')


class Mine(web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=4)
    
    @run_on_executor
    def get(self):
        self.set_header("Content-Type", 'application/json;charset="utf-8"')
        last_block = block_chain.last_block
        last_proof = last_block['proof']
        proof = block_chain.proof_of_word(last_proof)

        # 给工作量证明的节点提供奖励.
        # 发送者为 "0" 表明是新挖出的币
        block_chain.new_transaction(
            sender="0",
            recipient=node_identifier,
            amount=1,
        )

        # Forge the new Block by adding it to the chain
        block = block_chain.new_block(proof)

        res = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }
        self.write(json.dumps(res, ensure_ascii=False))


class Transactions(web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=4)
    
    @run_on_executor
    def post(self):
        self.set_header("Content-Type", 'application/json;charset="utf-8"')
        body = json.loads(self.request.body, strict=False)
        required = ['sender', 'recipient', 'amount']
        if not all(k in body.keys() for k in required):
            raise web.HTTPError(400, log_message="Missing values.")
        index = block_chain.new_transaction(body.get('sender'), body.get('recipient'), body.get('amount'))
        
        res = {'message': 'Transaction will be added to Block {index}'.format(index=index)}
        self.write(json.dumps(res, ensure_ascii=False))


class Chain(web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=4)
    
    @run_on_executor
    def get(self):
        self.set_header("Content-Type", 'application/json;charset="utf-8"')
        data = {
            'chain': block_chain.chain,
            'length': len(block_chain.chain),
        }
        self.write(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    try:
        setting = {"debug": True}
        application = wsgi.WSGIApplication([
            (r'/mine', Mine),
            (r'/transactions/new', Transactions),
            (r'/chain', Chain),
        ], **setting)
        tornado.options.parse_command_line()
        application.listen(port=8888, address="0.0.0.0")
        LOGGER.info("start listen http://{0}:{1}".format("0.0.0.0", 8888))
        ioloop.IOLoop.instance().start()
    except Exception as error:
        traceback.print_exc()
