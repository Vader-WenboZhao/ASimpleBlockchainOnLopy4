
import hashlib
import time
import ucrypto
import ubinascii
from hashlib import sha512
from name_key import *



DIFFICULTY = 0


def Modular_exponentiation(b,e,m): # 模幂运算
    if m == 1:
        return 0
    else:
        r = 1
        b %= m
        while e>0:
            if e % 2 == 1:
                r = (r*b) % m
            e = e >> 1
            b = (b**2) % m
        return r

def byteToHex(bytes):
    return ubinascii.hexlify(bytes)

def getHexHashStr(str):
    sha256 = hashlib.sha256()
    sha256.update(str.encode('utf-8'))
    byteResult = sha256.digest()
    result = byteToHex(byteResult)
    return result

def stringify(transactions):
    if type(transactions) == type([]):
        resultList = []
        for tran in transactions:
            resultList.append(tran.__dict__)
        return str(resultList)
    elif type(transactions) == type(''):
        return transactions
    else:
        return str(transactions.__dict__)


class Transaction:
    def __init__(self, comefrom, to, amount):
        self.comefrom = comefrom # 元组,(e,n)或者(d,n)
        self.to = to
        self.amount = amount

    def printInfo(self):
        print("\tcomefrom:", self.comefrom)
        print("\tto:", self.to)
        print("\tamount:", self.amount)

    def computeHash(self):
        return getHexHashStr(
            str(nameToPub[self.comefrom]) +
            str(nameToPub[self.to]) +
            str(self.amount))

    def sign(self, key): # key是元组,(d,n)或(e,n)
    # RSA sign the message
        hash = int.from_bytes(self.computeHash(), 'big')
        # self.signature = Modular_exponentiation(hash, d_sender, n_sender)
        print(" 📝 Signing...")
        self.signature = Modular_exponentiation(hash, key[0], key[1])


    def isValid(self):
        if self.comefrom == "":
            return True
        print(" 🔍 Validating...")
        hash = int.from_bytes(self.computeHash(), 'big')
        # hashFromSignature = Modular_exponentiation(self.signature, e_sender, n_sender)
        hashFromSignature = Modular_exponentiation(self.signature, nameToPub[self.comefrom][0], nameToPub[self.comefrom][1])
        return hash == hashFromSignature

'''    # 用pkcs8私钥签名
    def sign(self, key):
        self.signature = ucrypto.generate_rsa_signature(self.computeHash(), key)
        # self.signature = ucrypto.generate_rsa_signature(str(self.comefrom) + str(self.to) + str(self.amount), key)

    # 用pkcs8公钥验证
    def isValid(self):
        # 区块链发起的转账
        # self.comefrom是发送方的公钥
        if self.comefrom == "":
            return True
        # 其他原因发起的转账
        # 有问题 有问题 有问题 有问题 有问题 !!!
        message_decrypted = ucrypto.rsa_decrypt(self.signature, self.comefrom)
        return self.computeHash() == message_decrypted'''



class Block:
    def __init__(self, transactions, pre_hash):
        # data是transaction,对象的数组
        self.transactions = transactions
        self.pre_hash = pre_hash
        self.timestamp = time.time()  # lopy4只能获得启动之后的秒级时间戳
        self.nonce = 1  # 随机数
        self.hash = self.computeHash()

    def computeHash(self):
        return getHexHashStr(stringify(self.transactions) +
            str(self.pre_hash) +
            str(self.nonce) +
            str(self.timestamp))

    # 获取合法hash的要求(以前n位为0为例)
    def getAnswer(self, difficulty):
        # 开头前nb位为0的hash
        answer = ''
        for i in range(difficulty):
            answer += '0'
            i += 1
        return answer

    # 计算符合区块链难度要求的Hash
    def fish(self, difficulty):
        # 挖矿前验证所有transactions的合法性
        if not self.validateBlockTransactions():
            return False
        print(" 🎣 Fishing...")
        if difficulty==0:
            self.hash = self.computeHash()
            print(" Finish fishing *****", self.hash)
            return
        while True:
            self.hash = self.computeHash()
            # print(self.hash)
            if self.hash[0:difficulty] != self.getAnswer(difficulty):
                self.nonce += 1  # 找值
                if self.nonce%100==0:
                    print(" nonce=", self.nonce)
                continue
            else:
                break
        print(" Finish fishing *****", self.hash)

    def validateBlockTransactions(self):
        count = 0
        for transaction in self.transactions:
            count += 1
            print(" 🔍 Validating the", count, "th Transaction...")
            if not transaction.isValid():
                print("Invalid transaction is found in transactions!")
                return False
        print(" Valid block")
        return True

    def printInfo(self):
        for tran in self.transactions:
            print("\t" + str(tran.__dict__))
        print("\tpre_hash:", self.pre_hash)
        print("\thash:", self.hash)


class Chain:
    def __init__(self):
        self.chain = [self.createGenesisBlock()]
        self.transactionPool = []
        self.fisherReward = 50 # 产生50个比特币
        self.difficulty = DIFFICULTY # 区块链难度要求

    def createGenesisBlock(self):
        genesisTransactions = [Transaction("I'm genesis block","I'm genesis block",0)]
        genesisBlock = Block(genesisTransactions, '')
        return genesisBlock

    def getLatestBlock(self):
        # return self.chain[len(self.chain)-1]
        return self.chain[-1]

    # 添加transaction到transactionPool里
    def addTransaction(self, transaction):
        if not transaction.isValid():
            print("Transaction is invalid! Add transaction failed")
        else:
            print(" Valid transaction")
            self.transactionPool.append(transaction)

    def addBlockToChain(self, newBlock):
        newBlock.pre_hash = self.getLatestBlock().hash
        # newBlock.hash = newBlock.computeHash()
        newBlock.fish(self.difficulty)  # 代替上面那句注释
        self.chain.append(newBlock)

    def fishTransactionPool(self, fisherRewardAddress, mutex):
        # 挖矿
        newBlock = Block(self.transactionPool, self.getLatestBlock().hash)
        newBlock.fish(self.difficulty)

        # 发放矿工奖励
        print(" 🎣 Fishing is finished")
        fisherRewardTransaction = Transaction('', fisherRewardAddress, self.fisherReward)
        mutex.acquire()
        self.transactionPool.append(fisherRewardTransaction)

        # 添加区块到区块链
        # 清空transacPool
        self.chain.append(newBlock)
        self.transactionPool = []
        mutex.release()

        return (newBlock, fisherRewardTransaction)


    # 数据是否被篡改,该区块的pre_hash是否等于上一个区块的hash
    def validateChain(self):
        if(len(self.chain) == 1):
            if(self.chain[0].hash == getHexHashStr(self.chain[0].data)):
                return True
            return False
        else:
            for count in range(1, len(self.chain)):
                blockToValidate = self.chain[count]
                if not blockToValidate.validateBlockTransactions():
                    print("An invalid transaction is found!")
                    return False
                # 当前数据有无被篡改
                if blockToValidate.hash != blockToValidate.computeHash():
                    print("Block" + str(count) + "'s data has been tampered!")
                    return False
                preBlock = self.chain[count - 1]
                if blockToValidate.pre_hash != preBlock.hash:
                    print("Block " + str(count) +
                          "'s pre_hash isn't equal to the previous block's hash!")
                    return False
            return True

    def printInfo(self):
        print("********** Blocks **********")
        count = 1
        for block in self.chain:
            print("Block" + str(count) + ":")
            block.printInfo()
            count += 1
        count = 1
        print("********** TransactionPool **********")
        for tran in self.transactionPool:
            print("Transaction" + str(count) + ":")
            tran.printInfo()
            count += 1
