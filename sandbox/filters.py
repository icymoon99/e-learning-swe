import django_filters

from sandbox.models import ElSandboxInstance


class SandboxInstanceFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(lookup_expr="exact")
    status = django_filters.CharFilter(lookup_expr="exact")
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = ElSandboxInstance
        fields = ["type", "status", "name"]
