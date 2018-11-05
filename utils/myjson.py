import base64
import pickle


def dumps(mydict):
    """将字典转换成字符串"""
    #将字典转字节
    bytes_hex= pickle.dumps(mydict)
    #用base64里的b64encode加密
    bytes_64=base64.b64encode(bytes_hex)
    #转字符串
    return bytes_64.decode()

def loads(mystr):
    '''将字符串转换成字典'''
    #将字符串转换成字节
    # bytes_64 = mystr.encode()
    # bytes_64 = pickle.loads(mystr)
    # bytes_64 = mystr.encode()
    # #解密
    # bytes_hex=base64.b64decode(bytes_64)
    # #转字典
    # return pickle.loads(bytes_hex)


 # 将字符串转字节
    bytes_64 = mystr.encode()
    # 解密
    bytes_hex = base64.b64decode(bytes_64)
    # 转字典
    return pickle.loads(bytes_hex)
