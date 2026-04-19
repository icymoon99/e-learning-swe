#!/bin/bash
.venv/bin/python manage.py test \
  sandbox.tests.test_models.test_sandbox_instance \
  sandbox.tests.test_executors \
  sandbox.tests.test_backends.test_protocol \
  sandbox.tests.test_services \
  sandbox.tests.test_serializers \
  sandbox.tests.test_views.test_crud \
  sandbox.tests.test_filters \
  -v1 2>&1
echo "EXIT_CODE=$?"
