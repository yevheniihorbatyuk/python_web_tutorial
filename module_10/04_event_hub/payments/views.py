from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment, Invoice
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer,
    InvoiceSerializer, InvoiceCreateSerializer
)
from .tasks import process_payment


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'method']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        # Process payment asynchronously
        process_payment.delay(payment.id)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Refund a completed payment."""
        payment = self.get_object()
        if payment.status != Payment.Status.COMPLETED:
            return Response(
                {'error': 'Only completed payments can be refunded.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        payment.refund()
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        """Get payment receipt (invoice)."""
        payment = self.get_object()
        try:
            invoice = payment.invoice
            return Response(InvoiceSerializer(invoice).data)
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found for this payment.'},
                status=status.HTTP_404_NOT_FOUND
            )


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for Invoice model."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_sent']
    search_fields = ['invoice_number', 'payment__transaction_id']
    ordering_fields = ['issued_at']
    ordering = ['-issued_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Invoice.objects.all()
        return Invoice.objects.filter(payment__user=user)

    serializer_class = InvoiceSerializer

    @action(detail=True, methods=['post'])
    def mark_as_sent(self, request, pk=None):
        """Mark invoice as sent to user."""
        invoice = self.get_object()
        invoice.mark_as_sent()
        return Response(InvoiceSerializer(invoice).data)
