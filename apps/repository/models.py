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
    # 可用余额
    balance = models.DecimalField(verbose_name="可用余额", default=0, max_digits=10, decimal_places=2)

    # 不可用余额
    freeze_balance = models.DecimalField(verbose_name="不可用余额", default=0, max_digits=10, decimal_places=2)


class CompanyAuth(models.Model):
    """供应商认证"""
    company = models.OneToOneField(verbose_name="公司", to="Company", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="公司全称", max_length=64)
    unique_id = models.CharField(verbose_name="信用代码", max_length=64)
    licence_path = models.CharField(verbose_name="营业执照", max_length=64)
    legal_person = models.CharField(verbose_name="法人", max_length=32)
    legal_identity = models.CharField(verbose_name="法人身份证", max_length=64)
    legal_identity_front = models.CharField(verbose_name="身份证-人头", max_length=128)  # 文件路径
    legal_identity_back = models.CharField(verbose_name="身份证-国徽", max_length=128)  # 文件路径
    remark = models.TextField(verbose_name="审核备注", null=True, blank=True)


class TransactionRecord(models.Model):
    """交易记录"""
    company = models.ForeignKey(verbose_name="供应商", to="Company", on_delete=models.CASCADE)
    tran_type_choices = ((-1, "提现"), (1, "充值"))
    tran_type = models.SmallIntegerField(choices=tran_type_choices, verbose_name="转账类型")
    amount = models.DecimalField(verbose_name="金额", default=0, max_digits=10, decimal_places=2)
    ali_account = models.CharField(verbose_name="提现支付宝", max_length=64, null=True, blank=True)
    trans_id = models.CharField(verbose_name="订单号", max_length=64, db_index=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    trans_remark = models.TextField(verbose_name="交易备注", null=True, blank=True)
    pay_status_cls_map = {-1: "danger", 0: "primary", 1: "success"}
    pay_status_choices = ((-1, "已取消"), (0, "未支付"), (1, "已支付"))
    pay_status = models.SmallIntegerField(verbose_name="支付状态", choices=pay_status_choices, default=0)

    # 审核相关
    auditor_status_choices = ((-1, "审核失败"), (0, "待审核"), (1, "审核通过"))
    auditor_status = models.SmallIntegerField(verbose_name="审核", choices=auditor_status_choices, null=True,
                                              blank=True)
    auditor = models.ForeignKey(verbose_name="审核员", to="Administrator", on_delete=models.CASCADE, null=True,
                                blank=True)
    auditor_datetime = models.DateTimeField(verbose_name="审核时间", null=True, blank=True)
    auditor_remark = models.TextField(verbose_name="审核备注", null=True, blank=True)


class Administrator(models.Model):
    """管理员"""
    username = models.CharField(verbose_name="用户名", max_length=32, db_index=True)
    password = models.CharField(verbose_name="密码", max_length=64)
