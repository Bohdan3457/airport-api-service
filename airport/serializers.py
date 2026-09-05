from rest_framework import serializers
from django.db import transaction
from airport.models import(
    AirplaneType,
    Airport,
    Airplane,
    Route,
    Crew,
    Flight,
    Order,
    Ticket
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)

    class Meta(AirplaneSerializer.Meta):
        fields = AirplaneSerializer.Meta.fields


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

    class Meta(RouteSerializer.Meta):
        fields = RouteSerializer.Meta.fields


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew"
        )


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(read_only=True)
    airplane_name = serializers.CharField(source="airplane.name", read_only=True)
    airplane_capacity = serializers.IntegerField(
        source="airplane.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta(FlightSerializer.Meta):
        fields = (
            "id",
            "route",
            "airplane_name",
            "airplane_capacity",
            "departure_time",
            "arrival_time",
            "tickets_available",
        )

class FlightDetailSerializer(FlightSerializer):
    route = RouteListSerializer(read_only=True)
    airplane = AirplaneListSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta(FlightSerializer.Meta):
        fields = FlightSerializer.Meta.fields


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def validate(self, attrs):
        tickets = attrs.get("tickets", [])
        ticket_seats = []
        for ticket in tickets:
            seat_identifier = (ticket["flight"], ticket["row"], ticket["seat"])
            if seat_identifier in ticket_seats:
                raise serializers.ValidationError(
                    "You cannot book duplicate seats within the same order."
                )
            ticket_seats.append(seat_identifier)
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order
