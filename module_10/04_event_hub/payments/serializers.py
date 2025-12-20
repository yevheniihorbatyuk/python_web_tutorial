from rest_framework import serializers
from .models import Payment, Invoice


class PaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    booking_event = serializers.CharField(source='booking.event.title', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'booking', 'booking_event', 'user', 'user_name',
            'amount', 'currency', 'status', 'method',
            'transaction_id', 'reference_number',
            'created_at', 'processed_at', 'refunded_at',
            'error_message', 'metadata'
        )
        read_only_fields = ('transaction_id', 'created_at', 'processed_at', 'refunded_at', 'error_message')


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment records."""

    class Meta:
        model = Payment
        fields = ('booking', 'amount', 'method')

    def create(self, validated_data):
        user = self.context['request'].user
        booking = validated_data['booking']
        amount = validated_data.get('amount', booking.total_price)
        method = validated_data.get('method', Payment.Method.MOCK)

        # Generate unique transaction ID
        import uuid
        transaction_id = f"EVH-{uuid.uuid4().hex[:12].upper()}"

        payment = Payment.objects.create(
            booking=booking,
            user=user,
            amount=amount,
            currency='USD',
            method=method,
            transaction_id=transaction_id
        )

        return payment


class InvoiceSerializer(serializers.ModelSerializer):
    payment_id = serializers.IntegerField(source='payment.id', read_only=True)
    transaction_id = serializers.CharField(source='payment.transaction_id', read_only=True)
    event_title = serializers.CharField(source='payment.booking.event.title', read_only=True)
    user_name = serializers.CharField(source='payment.user.get_full_name', read_only=True)

    class Meta:
        model = Invoice
        fields = (
            'id', 'invoice_number', 'payment_id', 'transaction_id',
            'event_title', 'user_name',
            'billing_address', 'notes',
            'is_sent', 'issued_at', 'sent_at'
        )
        read_only_fields = ('invoice_number', 'issued_at', 'sent_at')


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invoices."""

    class Meta:
        model = Invoice
        fields = ('payment', 'billing_address', 'notes')

    def create(self, validated_data):
        import uuid
        payment = validated_data['payment']

        # Generate invoice number
        invoice_number = f"INV-{payment.transaction_id[-8:]}-{uuid.uuid4().hex[:4].upper()}"

        invoice = Invoice.objects.create(
            payment=payment,
            invoice_number=invoice_number,
            billing_address=validated_data['billing_address'],
            notes=validated_data.get('notes', '')
        )

        return invoice
