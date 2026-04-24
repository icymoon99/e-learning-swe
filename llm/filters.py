import django_filters

from .models import ElLLMProvider, ElLLMModel


class ElLLMProviderFilter(django_filters.FilterSet):
    class Meta:
        model = ElLLMProvider
        fields = ["enabled"]


class ElLLMModelFilter(django_filters.FilterSet):
    class Meta:
        model = ElLLMModel
        fields = ["provider", "enabled"]
