from blockChain import *


def dictToTransaction(dict):
    newTransaction = Transaction(dict['comefrom'], dict['to'], dict['amount'])
    return newTransaction


def chainToDict(myChain):
    chain = myChain.chain # blocks列表, 每个block还有transaction列表
    transactionPool = myChain.transactionPool # transactions列表
    fisherReward = myChain.fisherReward # int
    difficulty = myChain.difficulty # int

    chainList = []
    transactionPoolList = []
    transactionsList = []

    for block in chain:
        for transaction in block.transactions:
            transactionsList.append(transaction.__dict__)
        newBlock = block.__dict__
        newBlock['transactions'] = transactionsList
        chainList.append(newBlock)
        transactionsList = []

    for trans in transactionPool:
        transactionPoolList.append(trans.__dict__)

    result = {'chain':chainList, 'transactionPool':transactionPoolList, 'fisherReward':fisherReward, 'difficulty':difficulty}
    return result



def dictToChain(dict):
    newChain = Chain()
    newChain.chain = []
    newChain.fisherReward = int(dict['fisherReward'])
    newChain.difficulty = int(dict['difficulty'])

    chainList = dict['chain']
    for block in chainList:
        transactionsList = block['transactions']
        newTransactions = []
        for transaction in transactionsList:
            newTransaction = Transaction(transaction['comefrom'], transaction['to'], transaction['amount'])
            if transaction.get('signature'):
                newTransaction.signature = transaction['signature']
            newTransactions.append(newTransaction)
        newBlock = Block(newTransactions, block['pre_hash'])
        newBlock.timestamp = block['timestamp']
        newBlock.nonce = block['nonce']
        newBlock.hash = block['hash']
        newChain.chain.append(newBlock)

    transactionPoolList = dict['transactionPool']
    for trans in transactionPoolList:
        newTrans = Transaction(trans['comefrom'], trans['to'], trans['amount'])
        if trans.get('signature'):
            newTrans.signature = trans['signature']
        newChain.transactionPool.append(newTrans)

    return newChain
