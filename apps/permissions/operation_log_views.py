from rest_framework import serializers, viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import OperationLog


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = '__all__'
        read_only_fields = ('id', 'create_datetime')


class OperationLogCreateUpdateSerializer(serializers.ModelSerializer):
    """操作日志创建更新序列化器"""
    
    class Meta:
        model = OperationLog
        exclude = ('id', 'create_datetime')


class OperationLogViewSet(viewsets.ModelViewSet):
    """操作日志视图集"""
    queryset = OperationLog.objects.all().order_by('-create_datetime')
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['request_method', 'status', 'creator']
    search_fields = ['request_path', 'request_modular', 'request_msg']
    ordering_fields = ['create_datetime', 'request_method']
    ordering = ['-create_datetime']
    
    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return OperationLogCreateUpdateSerializer
        return OperationLogSerializer
    
    def perform_create(self, serializer):
        """创建时自动设置操作用户"""
        serializer.save(creator=self.request.user)