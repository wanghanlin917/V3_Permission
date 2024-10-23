from django.db import models


class Company(models.Model):
    """供应商"""
    username = models.CharField(verbose_name="企业简称", max_length=32)
    mobile = models.CharField(verbose_name="手机号码", max_length=11)
    email = models.CharField(verbose_name="邮箱", max_length=32, default="")
    password = models.CharField(verbose_name="密码", max_length=32)
    auth_type = models.SmallIntegerField(verbose_name="认证类型", choices=((1, "未认证"), (2, "认证中"), (3, "已认证")),
                                         default=1)
    ctime = models.DateTimeField(verbose_name="注册时间", auto_now_add=True)


class CompanyAuth(models.Model):
    """供应商认证"""
    company = models.ForeignKey(verbose_name="公司", to="Company", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="公司全称", max_length=64)
    unique_id = models.CharField(verbose_name="信用代码", max_length=64)
    licence_path = models.CharField(verbose_name="营业执照", max_length=64)
    legal_person = models.CharField(verbose_name="法人", max_length=32)
    legal_identity = models.CharField(verbose_name="法人身份证", max_length=64)
    legal_identity_front = models.CharField(verbose_name="身份证-人头", max_length=128)  # 文件路径
    legal_identity_back = models.CharField(verbose_name="身份证-国徽", max_length=128)  # 文件路径
    remark = models.TextField(verbose_name="审核备注", null=True, blank=True)
