import django_filters

from task.models import ElTask, ElTaskMemory


class ElTaskFilter(django_filters.FilterSet):
    class Meta:
        model = ElTask
        fields = ["status", "git_source"]


class TaskMemoryFilterSet(django_filters.FilterSet):
    """任务记忆过滤器"""

    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = ElTaskMemory
        fields = ["status"]
