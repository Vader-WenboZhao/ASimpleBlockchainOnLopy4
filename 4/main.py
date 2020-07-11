from network import LoRa
import socket
import time
import pycom
import json
import _thread
from blockChain import *
from convert import *
from name_key import *
from myrandom import *


pycom.heartbeat(False)





# 自己的私钥元组
f = open("/flash/lib/d_4.txt")
d = f.read()
f.close()
d = int(d)
myPri = (d, n4)



# LED灯闪烁
def blink(num = 3, period = .5, color = 0):
    """ LED blink """
    for i in range(0, num):
        pycom.rgbled(color)
        time.sleep(period)
        pycom.rgbled(0)

def sendTransaction(t, mutex):
    transToSend = t
    code = 0
    transToSend.sign(myPri)
    # 将转账记录加入wenboChain
    mutex.acquire()
    wenboChain.addTransaction(transToSend)
    mutex.release()
    trans_send = transToSend.__dict__
    # 提取出签名
    signature = str(trans_send['signature'])
    # 清空签名
    trans_send['signature'] = ''
    # 生成一个用于识别的6位的随机数作为编号
    code = RandomRange(100000, 999999)
    # 发出没签名的transaction JSON
    msg = {'transaction' : trans_send, 'type' : 1, 'code' : code}
    json_send = json.dumps(msg)
    #print(json_send)
    s1.send(json_send)
    # 停顿2s
    time.sleep(2)
    # 分两次发送送签名
    msg = {'sig':signature[:180], 'part':1, 'type':3, 'code' : code}
    json_send = json.dumps(msg)
    #print(json_send)
    s1.send(json_send)
    time.sleep(2)
    msg = {'sig':signature[180:], 'part':2, 'type':3, 'code' : code}
    json_send = json.dumps(msg)
    #print(json_send)
    s1.send(json_send)
    print(" A transaction is sent succesfully")



# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
# 消息发送套接字
s1 = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s1.setblocking(False)
# 消息接收套接字
s2 = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s2.setblocking(True)



# 转账记录的区块链
wenboChain = Chain()



T_UNIT = 10 # 时间单位5s


# 数据包接收线程
def receive_in(mutex):
    print("Receive in thread starts")
    global wenboChain
    waitingSig = {}
    waitingTransaction = {}
    while True:
        try:
            # 从套接字s2中取出新接收到的数据包, s2为阻塞套接字, 从中取出256字节的数据
            jsonData = s2.recv(256)
            recv_msg = json.loads(jsonData)

            # 更新wenboChain
            # 有新的区块链, 收到JSON: {'chain':..., 'type':0}
            # if recv_msg['type'] == 0:
            #     mutex.acquire()
            #     wenboChain = dictToChain(recv_msg['chain'])
            #     mutex.release()
            #     print(" WenboChain is created")

            # 有新的转账, 收到JSON: {'transaction':..., 'type':1, 'code':...}, 其中签名另行接收
            if recv_msg['type'] == 1:
                newTransaction = dictToTransaction(recv_msg['transaction'])
                # 提取出识别编号作为字典的键, 将新的Transaction添加到waitingTransaction里, 在waitingSig里创建等待接收的空的签名字典
                newCode = recv_msg['code']
                waitingTransaction[newCode] = newTransaction
                waitingSig[newCode] = {1:'', 2:''}

            # 有新的挖矿, 收到JSON: {'transaction':..., 'timestamp':..., 'nonce':..., 'hash':..., 'type':2}
            elif recv_msg['type'] == 2:
                # 挖矿是没有签名的, 因此不需要再另行接收签名
                newTransaction = dictToTransaction(recv_msg['transaction'])
                if newTransaction.isValid():
                    mutex.acquire()
                    wenboChain.addTransaction(newTransaction)
                    mutex.release()
                else:
                    print(" An invalid block!")
                    continue

                newBlock = Block(wenboChain.transactionPool, wenboChain.getLatestBlock().hash)
                newBlock.timestamp = recv_msg['timestamp']
                newBlock.nonce = recv_msg['nonce']
                newBlock.hash = recv_msg['hash']

                if newBlock.validateBlockTransactions():
                    mutex.acquire()
                    wenboChain.chain.append(newBlock)
                    wenboChain.transactionPool = []
                    mutex.release()
                    print(" A new block is added succesfully")
                else:
                    mutex.acquire()
                    wenboChain.transactionPool.pop()
                    mutex.release()
                    print(" An invalid block!")
                    continue

            # 收到签名, 分成两部分接收, JSON: {'sig':..., 'part':..., 'type':3, 'code':...}
            elif recv_msg['type'] == 3:
                # 提取出识别编号code
                recvCode = recv_msg['code']

                if recv_msg['part'] == 1:
                    waitingSig[recvCode][1] += recv_msg['sig']
                elif recv_msg['part'] == 2:
                    waitingSig[recvCode][2] += recv_msg['sig']
                if waitingSig[recvCode][1]!='' and waitingSig[recvCode][2]!='':
                    signature = waitingSig[recvCode][1] + waitingSig[recvCode][2]
                    waitingTransaction[recvCode].signature = int(signature)
                    if waitingTransaction[recvCode].isValid():
                        mutex.acquire()
                        wenboChain.addTransaction(waitingTransaction[recvCode])
                        mutex.release()
                        print(" A new transaction is added succesfully")
                    else:
                        print(" An invalid transaction!")
                    # 接收成功后删除对应的字典项
                    waitingSig.pop(recvCode)
                    waitingTransaction.pop(recvCode)


        except BaseException:
            print("Error in receive_in()")
            continue





# 数据包发送线程, 发送数据信息
def send_out(mutex):
    print("Send out thread starts")

    # initialize()

    global wenboChain


    # 两次模拟转账
    t1 = Transaction(4, 2, 9)
    t2 = Transaction(4, 3, 14)

    sendTransaction(t1, mutex)

    print("Send_out thread finishes")


    # 挖矿
    newAddedBlock, fisherRewardTransaction = wenboChain.fishTransactionPool(4, mutex)
    msg = {'transaction':fisherRewardTransaction.__dict__, 'timestamp':newAddedBlock.timestamp, 'nonce':newAddedBlock.nonce, 'hash':newAddedBlock.hash, 'type':2}
    #print(msg)
    json_send = json.dumps(msg)
    s1.send(json_send)
    print(" A block is sent succesfully")

    sendTransaction(t2, mutex)

    print("Send_out thread finishes")



mutex1 = _thread.allocate_lock()
mutex2 = _thread.allocate_lock()
rcv_thread = _thread.start_new_thread(receive_in, (mutex1,))
time.sleep(180)
send_out_thread = _thread.start_new_thread(send_out, (mutex2,))
time.sleep(240) # 240
wenboChain.printInfo()
