# from collections import OrderedDict
#
# from goods.models import GoodsChannel
#
#
# def get_goods_category():
#     '''
#     {
#             组编号（同频道）:{
#                 一级分类channels：[]
#                 二级分类sub_cats：[]
#             }
#         }
#         如：
#         {
#             1:{
#                 channels:[
#                     {手机},{相机},{数码}
#                 ],
#                 sub_cats:[二级分类]
#             },
#             2:{
#                 channels:[
#                     {电脑},{办公},{家用电器}
#                 ],
#                 sub_cats:[二级分类]
#             },
#             ....
#         }
#         '''
#     # todo
#     # 假如使用空的会怎样,打印一下
#     categories = OrderedDict()
#     channels = GoodsChannel.objects.all()
#     for channel in channels:
#         # 怎么表示组编号
#         # channel.group_id
#         # 怎么表示一级分类
#         # channel.category
#         if channel.group_id not in categories:
#             categories[channel.group_id] = {'channels': [], 'sub_cats': []}
#         # 添加一级分类
#         categories[channel.group_id]['channels'].append({
#             'id': channel.id,
#             'name': channel.category.name,
#             'url': channel.url
#         })
#
#         # 二级变量
#         sub_cats = channel.category.goodscategory_set.all()
#         # 添加二级分类
#         for sub in sub_cats:
#             sub.sub_cats = sub.goodscategory_set.all()
#
#             categories[channel.group_id]['sub_cats'].append(sub)
#
#     return categories
