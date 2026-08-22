from rest_framework import serializers
from .models import Cluster, Namespace, App

class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = ['id', 'name', 'address', 'token', 'created_at']
        extra_kwargs = {
            'token': {'write_only': True}
        }

class NamespaceSerializer(serializers.ModelSerializer):
    cluster_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Namespace
        fields = ['id', 'cluster_id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']
    
class AppSerializer(serializers.ModelSerializer):
    namespace_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = App
        fields = ['id', 'namespace_id', 'name', 'image', 'replicas', 'cpu', 'memory', 'created_at']
        read_only_fields = ['id', 'created_at']