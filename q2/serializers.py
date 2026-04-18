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


class ScheduleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    func = serializers.CharField()
    schedule_type = serializers.CharField()
    minutes = serializers.IntegerField(allow_null=True, required=False)
    repeats = serializers.IntegerField(allow_null=True, required=False, default=-1)
    next_run = serializers.DateTimeField(allow_null=True, read_only=True)
    cron = serializers.CharField(allow_null=True, required=False)
    task = serializers.CharField(allow_null=True, read_only=True)
    args = serializers.CharField(allow_null=True, required=False)
    kwargs = serializers.JSONField(allow_null=True, required=False)

    def create(self, validated_data):
        from django_q.models import Schedule
        return Schedule.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
