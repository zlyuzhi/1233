from django.db import models

# Create your models here.
#自关联的一对多

# area====>深圳市
# area.parant===>广东省
# area.parent_id===>广东省的id
# area.area_set====>area.subs



class Area(models.Model):
    '''行政区域的划分'''
    name =models.CharField(max_length=20)
    parent=models.ForeignKey('self',null=True,blank=True,related_name='subs')

    class Meta:
        db_table='tb_areas'
        verbose_name='收货地址'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name