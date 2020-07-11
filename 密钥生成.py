import Crypto.PublicKey.RSA
import Crypto.Random


path = "/Users/zhaowenbo/3rd_grade_3/物联网2020/"


for i in range(1, 5):
    x = Crypto.PublicKey.RSA.generate(1024)

    with open(path + "n_" + str(i) + ".txt", "w") as p:
        p.write(str(x.n))
    with open(path + "e_" + str(i) + ".txt", "w") as p:
        p.write(str(x.e))
    with open(path + "d_" + str(i) + ".txt", "w") as p:
        p.write(str(x.d))

    a = x.exportKey("PEM")  # 生成私钥
    b = x.publickey().exportKey()   # 生成公钥
    with open(path + "private_" + str(i) + ".pem", "wb") as p:
        p.write(a)
    with open(path + "public_" + str(i) + ".pem", "wb") as p:
        p.write(b)
