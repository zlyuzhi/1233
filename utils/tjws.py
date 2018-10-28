from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer

# 使用TimedJSONWebSignatureSerializer可以生成带有有效期的token

def dumps(data,expires):
    #创建对象
    serializer= TimedJSONWebSignatureSerializer(settings.SECRET_KEY,expires)
    #加密
    result =serializer.dumps(data).decode()
    return result

def loads(data,expires):
    #创建对象
    serializer =TimedJSONWebSignatureSerializer(settings.SECRET_KEY,expires)
    #解密
    try:
        data_dict =serializer.loads(data)
        return data_dict
    except:
        #抛出异常 超时
        return None