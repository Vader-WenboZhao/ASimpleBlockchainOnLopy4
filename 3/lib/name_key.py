# 4个节点的公钥
f = open("/flash/lib/publicKeys/e_1.txt")
e1 = f.read()
f.close()
e1 = int(e1)
f = open("/flash/lib/publicKeys/e_2.txt")
e2 = f.read()
f.close()
e2 = int(e2)
f = open("/flash/lib/publicKeys/e_3.txt")
e3 = f.read()
f.close()
e3 = int(e3)
f = open("/flash/lib/publicKeys/e_4.txt")
e4 = f.read()
f.close()
e4 = int(e4)

# 四个节点的模
f = open("/flash/lib/publicKeys/n_1.txt")
n1 = f.read()
f.close()
n1 = int(n1)
f = open("/flash/lib/publicKeys/n_2.txt")
n2 = f.read()
f.close()
n2 = int(n2)
f = open("/flash/lib/publicKeys/n_3.txt")
n3 = f.read()
f.close()
n3 = int(n3)
f = open("/flash/lib/publicKeys/n_4.txt")
n4 = f.read()
f.close()
n4 = int(n4)

# 公钥元组
pub1 = (e1, n1)
pub2 = (e2, n2)
pub3 = (e3, n3)
pub4 = (e4, n4)

# 公钥字典
nameToPub = {1:pub1, 2:pub2, 3:pub3, 4:pub4}
