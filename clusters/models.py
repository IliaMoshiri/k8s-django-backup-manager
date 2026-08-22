from django.db import models

class Cluster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Namespace(models.Model):
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, related_name='namespaces')
    name = models.CharField(max_length=63)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cluster', 'name')

    def __str__(self):
        return f"{self.name} ({self.cluster.name})"

class App(models.Model):
    namespace = models.ForeignKey(Namespace, on_delete=models.CASCADE, related_name='apps')
    name = models.CharField(max_length=63)
    image = models.CharField(max_length=255)
    replicas = models.IntegerField(default=1)
    cpu = models.CharField(max_length=50, default="100m")
    memory = models.CharField(max_length=50, default="128Mi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('namespace', 'name')

    def __str__(self):
        return f"{self.name} ({self.namespace.name})"