from rest_framework.permissions import IsAuthenticated
from airport.permissions import IsAdminOrReadOnly
from django.db.models import F, Count
from rest_framework import viewsets
from airport.filters import FlightFilter
from airport.models import (
    Airport,
    AirplaneType,
    Crew,
    Airplane,
    Route,
    Flight,
    Order
)
from airport.serializers import (
    AirportSerializer,
    AirplaneTypeSerializer,
    CrewSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    RouteSerializer,
    RouteListSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):

    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return self.serializer_class


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return self.serializer_class


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects
        .select_related("route__source", "route__destination", "airplane")
        .prefetch_related("crew")
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
            )
        )
    )
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = FlightSerializer
    filterset_class = FlightFilter

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return self.serializer_class


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related(
                "tickets__flight__route",
                "tickets__flight__airplane"
            )
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
