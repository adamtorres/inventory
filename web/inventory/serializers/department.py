from rest_framework import serializers

from .. import models as inv_models


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = inv_models.Department
        fields = '__all__'
