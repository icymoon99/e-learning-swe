import django_filters

from task.models import ElTask


class ElTaskFilter(django_filters.FilterSet):
    class Meta:
        model = ElTask
        fields = ["status", "git_source"]
