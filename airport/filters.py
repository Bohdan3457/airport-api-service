import django_filters
from airport.models import Flight


class FlightFilter(django_filters.FilterSet):
    departure_time = django_filters.DateFilter(
        field_name="departure_time", lookup_expr="date"
    )
    from_airport = django_filters.NumberFilter(field_name="route__source__id")
    to_airport = django_filters.NumberFilter(field_name="route__destination__id")

    class Meta:
        model = Flight
        fields = ["departure_time", "from_airport", "to_airport", "airplane"]
