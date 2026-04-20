import django_filters
from agent.models import ElAgent, ElAgentExecutionLog


class ElAgentFilter(django_filters.FilterSet):
    """Agent 配置过滤器"""

    status = django_filters.CharFilter(lookup_expr="exact")
    code = django_filters.CharFilter(lookup_expr="exact")
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = ElAgent
        fields = ["status", "code", "name"]


class ElAgentExecutionLogFilter(django_filters.FilterSet):
    """Agent 执行日志过滤器"""

    agent = django_filters.UUIDFilter(field_name="agent_id", lookup_expr="exact")
    status = django_filters.CharFilter(lookup_expr="exact")
    thread_id = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = ElAgentExecutionLog
        fields = ["agent", "status", "thread_id"]
