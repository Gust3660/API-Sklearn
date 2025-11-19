from rest_framework import serializers

class DatasetUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class DivideDatasetSerializer(serializers.Serializer):
    test_size = serializers.FloatField(default=0.2, min_value=0.01, max_value=0.99)
    random_state = serializers.IntegerField(default=42)

class PrepareDataSerializer(serializers.Serializer):
    pass

class TransformersSerializer(serializers.Serializer):
    pass
