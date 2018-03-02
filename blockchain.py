#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
 * Created by zbl on 18-3-2 上午9:28.
"""


class BlockChain(object):
    
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        
    def new_block(self):
        pass

    def new_transaction(self, sender, recipient, amount):
        """
        生成新交易信息，信息将加入到下一个待挖的区块中
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
    
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
    
        return self.last_block['index'] + 1
    
    @staticmethod
    def hash(block):
        pass
    
    @property
    def last_block(self):
        pass
