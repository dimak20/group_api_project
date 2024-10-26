from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter
)


book_list_create_schema = extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of books "
        "and allows filtering by several criteria",
        parameters=[
            OpenApiParameter(
                name="genres",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="<b>Filter books by genre name. </b>"
                "Case-insensitive. <br><i>Example: science</i></br>",
                required=False,
            ),
            OpenApiParameter(
                name="authors__first_name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="<b>Filter books by author's first name. </b>"
                "Case-insensitive. <br><i>Example: ray</i></br>",
                required=False,
            ),
            OpenApiParameter(
                name="authors__last_name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="<b>Filter books by author's last name. </b>"
                "Case-insensitive. <br><i>Example: brad</i></br>",
                required=False,
            ),
            OpenApiParameter(
                name="title",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="<b>Filter books by title. </b>"
                "Case-insensitive. <br><i>Example: wine</i></br>",
                required=False,
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="<b>ORDERING books by "
                            "title / year / author's last name. </b>"
                "Case-insensitive. <br><i>Example: -year</i></br>",
                required=False,
            ),
        ],
    ),
)
