import django_filters

from .models import ElGitSource


class ElGitSourceFilter(django_filters.FilterSet):
    class Meta:
        model = ElGitSource
        fields = ["platform"]
