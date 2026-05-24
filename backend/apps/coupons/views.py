from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Coupon
from .serializers import CouponSerializer, CouponCreateSerializer, CouponIssueSerializer
from apps.core.permissions import IsAdminUser


class CouponViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get'], detail=False)
    def my(self, request):
        status_param = request.query_params.get('status')
        qs = Coupon.objects.filter(user=request.user)
        if status_param:
            qs = qs.filter(status=status_param)
        return Response(CouponSerializer(qs, many=True).data)


class CouponAdminViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return CouponCreateSerializer
        if self.action == 'issue':
            return CouponIssueSerializer
        return CouponSerializer

    @action(methods=['post'], detail=False, url_path='issue')
    def issue(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        created = []
        for user_id in data['user_ids']:
            for _ in range(data['count_per_user']):
                coupon = Coupon.objects.create(
                    type=data['type'],
                    discount_value=data['discount_value'],
                    min_order_amount=data['min_order_amount'],
                    start_time=data['start_time'],
                    end_time=data['end_time'],
                    status='unused',
                    user_id=user_id,
                )
                created.append(coupon)

        return Response(CouponSerializer(created, many=True).data, status=status.HTTP_201_CREATED)
