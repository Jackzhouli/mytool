from django.db import models


class UserInfo(models.Model):
    """
    用户表
    """
    nid = models.BigAutoField(primary_key=True)
    #  BigAutoField(AutoField)bigint自增列，必须填入参数 primary_key=True
    username = models.CharField(verbose_name="用户名", max_length=32, unique=True)
    password = models.CharField(verbose_name="密码", min_length=6, max_length=64)
    nickname = models.CharField(verbose_name="用户昵称", max_length=64)
    email = models.EmailField(verbose_name="邮箱", unique=True)
    avatar = models.ImageField(verbose_name="头像")
    create_time = models.DateTimeField(verbose_name="注册时间", auto_now_add=True)
    """
    此处是一个重要点，DateTimeField中有两个方法 1，auto_now_add和auto_now 两者默认值都为False。
    auto_now_add = True，字段在实例第一次保存的时候会保存当前时间，不管你在这里是否对其赋值。但是之后的save()
    是可以手动赋值的。也就是新实例化一个model，想手动存其他时间，就需要对该实例save()
    之后赋值然后再save()。
    auto_now=Ture，字段保存时会自动保存当前时间，但要注意每次对其实例执行save()的时候都会将当前时间保存，
    也就是不能再手动给它存非当前时间的值。
    要记住当时在这里饶了很久！！
    """
    fans = models.ManyToManyField(verbose_name="粉丝团",
                                  to='UserInfo',
                                  through='UserFans',
                                  related_name='f',
                                  through_fields=('user', 'follower'))
    """
    ManyToManyField(RelatedField)
    to,                         # 要进行关联的表名
    related_name=f,          # 反向操作时，使用的字段名f，用于代替 【表名_set】 如： obj.表名_set.all()
    through=UserFans,               # 自定义第三张表时，使用字段用于指定关系表
    through_fields=('user', 'follower'),        # 自定义第三张表时，使用字段用于指定关系表中那些字段做多对多关系表
    """


class UserFans(models.Model):
    """
    互粉关系表
    """
    user = models.ForeignKey(verbose_name='博主', to='UserInfo', to_field='nid', related_name='users')
    follower = models.ForeignKey(verbose_name='粉丝', to='UserInfo', to_field='nid', related_name='followers')

    class Meta:  # 在互粉表中设置联合唯一索引
        unique_together = [
            ('user', 'follower'),
        ]


class Blog(models.Model):
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name="个人文章标题", max_length=64,)
    site = models.CharField(verbose_name="文章的前缀", max_length=32, unique=True)
    theme = models.CharField(verbose_name="blog的主题", max_length=32)
    user = models.OneToOneField(to='UserInfo', to_field=nid)
    # OneToOneField适用于一对一的操作，博客和用户是一对一的，to_field和UserInfo的nid建立关系


class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)  # 文章数不可能太多，此时用AutoField足够了
    title = models.CharField(verbose_name='分类标题', max_length=32)
    blog = models.ForeignKey(verbose_name='所属blog', to='Blog', to_field='nid')  # 开通博客才能创建自己的共有分类
    """    一对多：models.ForeignKey(其他表)
    多对多：models.ManyToManyField(其他表)
    一对一：models.OneToOneField(其他表)
    """


class Article(models.Model):
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='文章标题', max_length=128)
    summary = models.CharField(verbose_name='文章简介', max_length=255)
    read_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')
    category = models.ForeignKey(verbose_name='文章类型', to='Category', to_field='nid', null=True)
    type_choices = [
        (1, "Python"),
        (2, "Linux"),
        (3, "OpenStack"),
        (4, "GoLang"),
    ]  # 因为大的标签都是固定的，所以直接做一个固定的选择
    article_type_id = models.IntegerField(choices=type_choices, default=None)

    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )
    # 文章内容较大，因此用额外的文章详细表节省性能


class ArticleDetail(models.Model):
    """
    文章详细表
    """
    content = models.TextField(verbose_name='文章内容', )
    article = models.OneToOneField(verbose_name='所属文章', to='Article', to_field='nid')


class UpDown(models.Model):
    """
    文章顶或踩
    """
    article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid')
    user = models.ForeignKey(verbose_name='赞或踩用户', to='UserInfo', to_field='nid')
    up = models.BooleanField(verbose_name='是否赞')  # BooleanField是布尔值类型的

    class Meta:
        unique_together = [
            ('article', 'user'),
        ]


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')


class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    reply = models.ForeignKey(verbose_name='回复评论', to='self', related_name='back', null=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid')
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid')


class Article2Tag(models.Model):
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid')
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid')

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]














