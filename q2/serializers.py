from rest_framework import serializers


class TaskSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    func = serializers.CharField()
    args = serializers.CharField(allow_null=True)
    kwargs = serializers.JSONField(allow_null=True)
    result = serializers.JSONField(allow_null=True)
    started = serializers.DateTimeField(allow_null=True)
    stopped = serializers.DateTimeField(allow_null=True)
    success = serializers.BooleanField(allow_null=True)
    attempt_count = serializers.IntegerField()
