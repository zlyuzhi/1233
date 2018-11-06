from django_redis import get_redis_connection

from utils import myjson


def merge_cart_cookie_to_redis(request, user_id, response):
    """
       合并请求用户的购物车数据，将未登录保存在cookie里的保存到redis中
       遇到cookie与redis中出现相同的商品时以cookie数据为主，覆盖redis中的数据
       :param request: 用户的请求对象
       :param user_id: 当前登录的用户
       :param response: 响应对象，用于清楚购物车cookie
       :return:
       """
    # 读取cookie中购物车的数据
    cart_str = request.COOKIES.get('cart')
    if cart_str is None:
        return response
    cart_dict = myjson.loads(cart_str)

    # 遍历,写入redis中
    redis_cli = get_redis_connection('cart')
    key_cart = 'cart_%d' % user_id
    key_selected = 'cart_selected_%d' % user_id

    # 获取管道
    redis_pipeline = redis_cli.pipeline()
    for sku_id, sku_dict in cart_dict.items():
        # hash存商品编号,数量
        redis_pipeline.hset(key_cart, sku_id, sku_dict['count'])
        # set根据选中状态存商品编号
        if sku_dict['selected']:
            redis_pipeline.sadd(key_selected, sku_id)
        else:
            redis_pipeline.srem(key_selected, sku_id)
    # 执行管道中的命令
    redis_pipeline.execute()

    # 3 删除cookie中的购物车数据
    response.set_cookie('cart', '', max_age=0)
    return response
