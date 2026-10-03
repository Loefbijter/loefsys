"""Shared admin helpers for exporting and filtering model data."""
# ruff: noqa: PLR0915,PLR0912,PLC0415,N806,N813

from __future__ import annotations

from io import BytesIO

from django.contrib import admin
from django.db import models
from django.http import HttpResponse
from django.urls import path
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from openpyxl import Workbook


class ExportableAdminMixin:
    """Mixin that exposes Excel export for filtered admin record sets."""

    change_list_template = "admin/change_list_export.html"
    actions = ("export_as_excel",)
    _max_default_list_filters = 4

    def get_urls(self):
        """Return the admin URLs, including the export endpoint."""
        urls = super().get_urls()
        export_url = path(
            "export_excel/",
            self.admin_site.admin_view(self.export_filtered_queryset),
            name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_export_excel",
        )
        return [export_url, *urls]

    def _user_can_export(self, request):
        """Return True if the given request user is authorized to export this model.

        Authorization rules:
        - superusers always allowed
        - users with model-specific export permission are allowed
          using '<app_label>.export_<modelname>'
        """
        user = getattr(request, "user", None)
        if not user:
            return False
        if getattr(user, "is_superuser", False):
            return True
        perm = f"{self.model._meta.app_label}.export_{self.model._meta.model_name}"
        try:
            return user.has_perm(perm)
        except Exception:
            # conservative: deny if permission system not available
            return False

    def changelist_view(self, request, extra_context=None):
        """Inject a flag into the change-list context for export permission."""
        extra_context = dict(extra_context or {})
        extra_context.setdefault("can_export", self._user_can_export(request))
        return super().changelist_view(request, extra_context=extra_context)

    def get_actions(self, request):
        """Remove the export action when the user is not authorized."""
        actions = super().get_actions(request)
        if "export_as_excel" in actions and not self._user_can_export(request):
            actions.pop("export_as_excel", None)
        return actions

    def _register_dashboard_url(self):
        """Register dashboard JSON endpoint on the admin site.

        This is registered lazily so importing admin_helpers doesn't alter the
        default admin urls unless the module is imported by site admin code
        (which it is from many admin modules in this project).
        """

        def dashboard_view(request):
            """Return KPI data used by the admin dashboard as JSON.

            Ensure only active staff users may access this endpoint.
            """
            from dateutil.relativedelta import relativedelta
            from django.core.exceptions import PermissionDenied
            from django.db.models import Count
            from django.http import JsonResponse
            from django.utils import timezone

            # Explicitly ensure the requesting user is an active staff member.
            # admin.site.admin_view already applies staff checks, but do a double-check
            # so this endpoint cannot be accidentally exposed without the admin wrapper.
            user = getattr(request, "user", None)
            if (
                not user
                or not getattr(user, "is_active", False)
                or not getattr(user, "is_staff", False)
            ):
                raise PermissionDenied

            # Lazy imports of models to avoid circular imports at import-time
            try:
                from loefsys.members.models import (
                    UserSkippership as user_skippership_model,
                )
            except Exception:
                user_skippership_model = None
            try:
                from loefsys.reservations.models import (
                    BoatDamageRecord as boat_damage_model,
                    Reservation as reservation_model,
                )
            except Exception:
                reservation_model = None
                boat_damage_model = None
            try:
                from loefsys.events.models import Event as event_model
                from loefsys.events.models.choices import (
                    EventCategories as event_categories_model,
                )
            except Exception:
                event_model = None
                event_categories_model = None

            try:
                now = timezone.now()
                # Start at beginning of current month
                first_of_month = now.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                # last N months to show in trend charts
                months = []
                labels = []
                N = 6
                for i in range(N - 1, -1, -1):
                    dt = first_of_month - relativedelta(months=i)
                    months.append(dt)
                    labels.append(dt.strftime("%Y-%m"))

                def month_range(dt):
                    start = dt
                    end = dt + relativedelta(months=1)
                    return start, end

                # New skippers per month and breakdown by skippership type
                skippers_series = []
                skippers_total = 0
                skippers_by_type = {}
                skippers_series_by_type = {}
                skippership_label_map = {}
                if user_skippership_model is not None:
                    # gather available skipperships and labels
                    try:
                        Skippership = user_skippership_model._meta.get_field(
                            "skippership"
                        ).remote_field.model
                        skippership_qs = Skippership.objects.all()
                        for s in skippership_qs:
                            key = str(s.pk)
                            skippership_label_map[key] = str(s.name)
                            skippers_by_type[key] = 0
                            skippers_series_by_type[key] = [0] * len(months)
                    except Exception:
                        # fallback: leave maps empty if fetching skipperships fails
                        skippership_label_map = {}
                        skippers_by_type = {}
                        skippers_series_by_type = {}

                    for idx, dt in enumerate(months):
                        start, end = month_range(dt)
                        cnt = user_skippership_model.objects.filter(
                            since__gte=start.date(), since__lt=end.date()
                        ).count()
                        skippers_series.append(cnt)

                        # per-type counts for this month
                        try:
                            grouped = (
                                user_skippership_model.objects.filter(
                                    since__gte=start.date(), since__lt=end.date()
                                )
                                .values("skippership")
                                .annotate(cnt=Count("id"))
                            )
                            for g in grouped:
                                key = str(g.get("skippership"))
                                # ensure key exists in maps
                                if key not in skippers_series_by_type:
                                    skippers_series_by_type[key] = [0] * len(months)
                                skippers_series_by_type[key][idx] = g.get("cnt", 0)
                                if idx == len(months) - 1:
                                    skippers_by_type[key] = skippers_by_type.get(
                                        key, 0
                                    ) + g.get("cnt", 0)
                        except Exception:
                            # ignore per-type grouping errors for resilience
                            pass

                    # current month total
                    skippers_total = skippers_series[-1] if skippers_series else 0

                # Reservations per month
                reservations_series = []
                reservations_total = 0
                pending_requests = 0
                if reservation_model is not None:
                    for dt in months:
                        start, end = month_range(dt)
                        cnt = reservation_model.objects.filter(
                            date_of_creation__gte=start, date_of_creation__lt=end
                        ).count()
                        reservations_series.append(cnt)

                    reservations_total = (
                        reservations_series[-1] if reservations_series else 0
                    )

                    try:
                        pending_requests = reservation_model.objects.filter(
                            request_status=reservation_model.RequestStatus.PENDING
                        ).count()
                    except Exception:
                        pending_requests = 0

                # Damage records per month
                damage_series = []
                damage_total = 0
                damage_by_type = {}
                if boat_damage_model is not None:
                    for idx, dt in enumerate(months):
                        start, end = month_range(dt)
                        qs_month = boat_damage_model.objects.filter(
                            created__gte=start, created__lt=end
                        )
                        cnt = qs_month.count()
                        damage_series.append(cnt)

                        # for the latest month also prepare breakdown by boat type
                        if idx == len(months) - 1:
                            grouped = qs_month.values("boat__type__name").annotate(
                                cnt=Count("id")
                            )
                            for g in grouped:
                                typename = g.get("boat__type__name") or "Unknown"
                                damage_by_type[str(typename)] = g.get("cnt", 0)

                    damage_total = damage_series[-1] if damage_series else 0

                # Events that have taken place (events with end < now)
                # partition by category
                events_by_category = {}
                events_series_by_category = {}
                event_total = 0
                # default empty mapping for labels if events model not available
                category_label_map = {}
                if event_model is not None and event_categories_model is not None:
                    # categories mapping
                    categories = []
                    for choice in event_categories_model:
                        categories.append((choice.value, choice.label))
                    # per-category totals (for current month counts)
                    # and historical series
                    # prepare category mappings and initialize series
                    category_label_map = {}
                    for value, label in categories:
                        key = str(value)
                        events_by_category[key] = 0
                        events_series_by_category[key] = [0] * len(months)
                        category_label_map[key] = label

                    # count events per month and category
                    for idx, dt in enumerate(months):
                        start, end = month_range(dt)
                        # events that ended in this month
                        qs = event_model.objects.filter(end__gte=start, end__lt=end)
                        qs = qs.filter(end__lt=now)
                        grouped = qs.values("category").annotate(cnt=Count("id"))
                        for g in grouped:
                            key = str(g.get("category"))
                            default_series = [0] * len(months)
                            series_list = events_series_by_category.setdefault(
                                key, default_series
                            )
                            series_list[idx] = g.get("cnt", 0)
                            # only add to total for current (last) month
                            if idx == len(months) - 1:
                                prev = events_by_category.get(key, 0)
                                events_by_category[key] = prev + g.get("cnt", 0)

                    # sum totals for current month
                    event_total = sum(events_by_category.values())

                    # also compute past month (previous calendar month)
                    # and upcoming month (next calendar month)
                    try:
                        prev_start = first_of_month - relativedelta(months=1)
                        prev_end = first_of_month
                        next_start = first_of_month + relativedelta(months=1)
                        next_end = next_start + relativedelta(months=1)

                        # initialize with all known categories to ensure consistent keys
                        known_category_keys = list(category_label_map.keys()) or list(
                            events_by_category.keys()
                        )
                        past_month_by_category = {k: 0 for k in known_category_keys}
                        upcoming_month_by_category = {k: 0 for k in known_category_keys}

                        # past: events that ended in the previous month
                        grouped_past = (
                            event_model.objects.filter(
                                end__gte=prev_start, end__lt=prev_end
                            )
                            .values("category")
                            .annotate(cnt=Count("id"))
                        )
                        for g in grouped_past:
                            past_month_by_category[str(g.get("category"))] = g.get(
                                "cnt", 0
                            )

                        # upcoming: events that start in the next month
                        grouped_upcoming = (
                            event_model.objects.filter(
                                start__gte=next_start, start__lt=next_end
                            )
                            .values("category")
                            .annotate(cnt=Count("id"))
                        )
                        for g in grouped_upcoming:
                            upcoming_month_by_category[str(g.get("category"))] = g.get(
                                "cnt", 0
                            )
                    except Exception:
                        past_month_by_category = {}
                        upcoming_month_by_category = {}

                payload = {
                    "labels": labels,
                    "skippers": {
                        "series": skippers_series,
                        "current_month": skippers_total,
                        "by_type": skippers_by_type,
                        "series_by_type": skippers_series_by_type,
                        "type_labels": skippership_label_map,
                    },
                    "reservations": {
                        "series": reservations_series,
                        "current_month": reservations_total,
                        "pending_requests": pending_requests,
                    },
                    "damage": {
                        "series": damage_series,
                        "current_month": damage_total,
                        "by_type": damage_by_type,
                    },
                    "events": {
                        "by_category": events_by_category,
                        "series_by_category": events_series_by_category,
                        "category_labels": category_label_map,
                        "current_month": event_total,
                        "past_month_by_category": past_month_by_category,
                        "upcoming_month_by_category": upcoming_month_by_category,
                    },
                }

                return JsonResponse(payload)
            except Exception as exc:
                # Log and return a safe minimal payload
                # so the admin page can still render
                import logging

                logging.exception("Failed to build admin dashboard payload")
                minimal = {
                    "labels": [],
                    "skippers": {"series": [], "current_month": 0},
                    "reservations": {
                        "series": [],
                        "current_month": 0,
                        "pending_requests": 0,
                    },
                    "damage": {"series": [], "current_month": 0, "by_type": {}},
                    "events": {
                        "by_category": {},
                        "series_by_category": {},
                        "category_labels": {},
                        "current_month": 0,
                    },
                    "error": str(exc),
                }
                return JsonResponse(minimal, status=200)

        # Register the URL only once
        from django.urls import path

        if getattr(admin.site, "_dashboard_registered", False):
            return None

        original_get_urls = admin.site.get_urls

        def _get_urls():
            # call the original get_urls and prepend our dashboard endpoint
            orig_urls = original_get_urls()
            dashboard_pattern = path(
                "dashboard-data/",
                admin.site.admin_view(dashboard_view),
                name="admin-dashboard-data",
            )
            return [dashboard_pattern, *orig_urls]

        admin.site.get_urls = _get_urls
        admin.site._dashboard_registered = True

        # call once so it's registered immediately
        # (force evaluation by accessing admin urls)
        _ = admin.site.urls
        return None

    def get_list_filter(self, request):
        """Provide a default list filter when none is specified."""
        if self.list_filter:
            return super().get_list_filter(request)

        filters: list[str] = []
        for field in self.model._meta.concrete_fields:
            if field.name == "id":
                continue
            if field.choices:
                filters.append(field.name)
            elif isinstance(
                field,
                (
                    models.BooleanField,
                    models.DateField,
                    models.DateTimeField,
                    models.ForeignKey,
                    models.OneToOneField,
                ),
            ):
                filters.append(field.name)

            if len(filters) >= self._max_default_list_filters:
                break

        self.list_filter = tuple(filters)
        return super().get_list_filter(request)

    @admin.action(description=_("Export selected rows to Excel"))
    def export_as_excel(self, request, queryset):
        """Export the selected rows to an Excel workbook.

        Only allow this action for superusers or users with the model-specific
        export permission ("<app>.export_<model>").
        """
        from django.core.exceptions import PermissionDenied

        if not self._user_can_export(request):
            raise PermissionDenied
        # optionally: log the export here (audit)
        return self._export_queryset(queryset)

    def export_filtered_queryset(self, request):
        """Export only rows visible after the current changelist filters."""
        from django.core.exceptions import PermissionDenied

        if not self._user_can_export(request):
            raise PermissionDenied
        changelist = self.get_changelist_instance(request)
        queryset = changelist.get_queryset(request)
        return self._export_queryset(queryset)

    def _export_queryset(self, queryset):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = str(self.model._meta.verbose_name_plural)[:31]

        fields = self.get_export_fields()
        sheet.append([str(field.verbose_name).capitalize() for field in fields])

        for obj in queryset:
            row = [self._render_export_value(obj, field) for field in fields]
            sheet.append(row)

        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        filename = f"{slugify(self.model._meta.verbose_name_plural)}.xlsx"
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    def get_export_fields(self):
        """Return the fields that should be exported to Excel."""
        return [*self.model._meta.concrete_fields, *self.model._meta.many_to_many]

    @staticmethod
    def _render_export_value(obj, field):
        if field.many_to_many:
            return ", ".join(str(item) for item in getattr(obj, field.name).all())

        raw_value = getattr(obj, field.name)
        if raw_value is None:
            return ""
        if isinstance(raw_value, models.Model):
            return str(raw_value)
        return str(raw_value)


class ExportableModelAdmin(ExportableAdminMixin, admin.ModelAdmin):
    """A ModelAdmin that supports Excel export and default list filters."""

    def __init__(self, *args, **kwargs):
        # ensure dashboard URL gets registered once (non-blocking)
        try:
            self._register_dashboard_url()
        except Exception:
            # don't block admin initialization on dashboard registration errors
            pass
        super().__init__(*args, **kwargs)
