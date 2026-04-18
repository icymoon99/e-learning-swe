from django.utils.translation import gettext_lazy as _
from ..models import ElUser


class ElUserAuthBackend:
    """
    自定义认证后端，支持使用用户名或手机号登录
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        验证用户名/手机号和密码
        """
        if username is None or password is None:
            return None
        
        try:
            # 尝试通过用户名查找用户
            user = ElUser.objects.get(username=username)
        except ElUser.DoesNotExist:
            try:
                # 尝试通过手机号查找用户
                user = ElUser.objects.get(phone=username)
            except ElUser.DoesNotExist:
                # 用户不存在
                return None
        
        # 验证密码
        if user.check_password(password):
            return user
        
        # 密码错误
        return None
    
    def get_user(self, user_id):
        """
        根据用户ID获取用户
        """
        try:
            return ElUser.objects.get(pk=user_id)
        except ElUser.DoesNotExist:
            return None