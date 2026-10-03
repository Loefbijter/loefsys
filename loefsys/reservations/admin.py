"""Admin configuration for the Reservation and Log models."""

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme, urlencode
from django.utils.translation import gettext_lazy as _

from loefsys.admin_helpers import ExportableModelAdmin

from .models import (
    BoatDamageRecord,
    BoatLogbook,
    ReservableBoat,
    ReservableMaterial,
    ReservableRoom,
    ReservableType,
    Reservation,
)

admin.site.register(ReservableType, ExportableModelAdmin)
admin.site.register(ReservableBoat, ExportableModelAdmin)
admin.site.register(ReservableMaterial, ExportableModelAdmin)
admin.site.register(ReservableRoom, ExportableModelAdmin)
admin.site.register(BoatDamageRecord, ExportableModelAdmin)
admin.site.register(BoatLogbook, ExportableModelAdmin)


@admin.register(Reservation)
class ReservationAdmin(ExportableModelAdmin):
    """Admin interface for reservations."""

    change_list_template = "admin/reservations/reservation/change_list.html"

    list_display = (
        "reservable",
        "user",
        "start",
        "end",
        "request_status",
        "date_of_creation",
        "evaluation_actions",
    )
    list_filter = ("request_status", "reservable__location", "reservable__type")
    search_fields = (
        "reservable__name",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    ordering = ("-date_of_creation",)
    readonly_fields = ("date_of_creation",)
    fieldsets = (
        (
            _("Reservation details"),
            {"fields": ("reservable", "user", "start", "end", "date_of_creation")},
        ),
        (_("Approval"), {"fields": ("request_status", "denial_reason")}),
    )

    #: Inline style that makes a <button> look like the plain text links admin
    #: list columns otherwise use (e.g. the reservable column), so Accept fits
    #: visually with Deny/Change without needing an extra stylesheet.
    _LINK_BUTTON_STYLE = (
        "background:none;border:none;padding:0;margin:0;font:inherit;"
        "color:var(--link-fg,#447e9b);text-decoration:underline;cursor:pointer;"
    )

    def get_readonly_fields(self, _request, obj=None):
        """Keep the reservation details editable on add but lock them after creation."""
        if obj is None:
            return self.readonly_fields

        return (*self.readonly_fields, "reservable", "user", "start", "end")

    def changelist_view(self, request, extra_context=None):
        """Expose ``RequestStatus`` so the change-list template can spot pending rows.

        Used to render one standalone accept form per pending reservation, placed
        outside the changelist's own bulk-action form (see the template).
        """
        extra_context = dict(extra_context or {})
        extra_context["RequestStatus"] = Reservation.RequestStatus
        return super().changelist_view(request, extra_context=extra_context)

    def get_list_display(self, request):
        """Bind the current request into the evaluation-actions column.

        ``list_display`` callables are only ever invoked with the row object, so the
        request is bound here (per-request, via a small closure) rather than stashed
        on ``self``, which would not be safe across concurrent requests. A plain
        function is used instead of ``functools.partial`` because the admin's column
        header rendering expects the callable to have a ``__name__``.
        """
        display = list(super().get_list_display(request))
        if "evaluation_actions" in display:
            render_actions = self.evaluation_actions

            def evaluation_actions(obj):
                return render_actions(request, obj)

            evaluation_actions.short_description = render_actions.short_description
            display[display.index("evaluation_actions")] = evaluation_actions
        return display

    def get_urls(self):
        """Add the endpoints used to accept, deny or change a reservation's status."""
        custom = [
            path(
                "<int:object_id>/accept/",
                self.admin_site.admin_view(self.accept_view),
                name="reservations_reservation_accept",
            ),
            path(
                "<int:object_id>/evaluate/",
                self.admin_site.admin_view(self.evaluate_view),
                name="reservations_reservation_evaluate",
            ),
        ]
        return custom + super().get_urls()

    def _safe_next_url(self, request, candidate):
        """Return ``candidate`` if safe to redirect to locally, else the changelist."""
        changelist_url = reverse("admin:reservations_reservation_changelist")
        if candidate and url_has_allowed_host_and_scheme(
            candidate, allowed_hosts={request.get_host()}
        ):
            return candidate
        return changelist_url

    def accept_view(self, request, object_id):
        """Immediately accept a pending reservation, without leaving the change list.

        POST-only, submitted by the standalone form the change-list template renders
        for each pending row (see ``changelist_view`` and the template it uses) -
        deliberately outside the changelist's own bulk-action form, since a ``<form>``
        nested inside another is invalid HTML and gets silently dropped by browsers.
        """
        if not self.has_change_permission(request):
            raise PermissionDenied

        reservation = get_object_or_404(Reservation, pk=object_id)
        next_url = self._safe_next_url(request, request.POST.get("next"))

        reservation.request_status = Reservation.RequestStatus.APPROVED
        reservation.denial_reason = ""
        try:
            reservation.full_clean()
        except ValidationError as exc:
            self.message_user(request, "; ".join(exc.messages), level=messages.ERROR)
        else:
            reservation.save()
            self.message_user(request, _("Reservation accepted."))

        return redirect(next_url)

    def evaluate_view(self, request, object_id):
        """Show and process the deny/change-status form for a reservation.

        Used both for denying a pending reservation (a reason is required) and for
        changing the status of an already-evaluated one.
        """
        if not self.has_change_permission(request):
            raise PermissionDenied

        reservation = get_object_or_404(Reservation, pk=object_id)
        next_url = self._safe_next_url(
            request, request.POST.get("next") or request.GET.get("next")
        )
        error = None

        if request.method == "POST":
            status = request.POST.get("status")
            denial_reason = request.POST.get("denial_reason", "").strip()

            if status == "accepted":
                reservation.request_status = Reservation.RequestStatus.APPROVED
                reservation.denial_reason = ""
            elif status == "denied":
                reservation.request_status = Reservation.RequestStatus.DENIED
                reservation.denial_reason = denial_reason
            else:
                error = _("Kies een status.")

            if error is None:
                try:
                    reservation.full_clean()
                except ValidationError as exc:
                    error = "; ".join(exc.messages)
                else:
                    reservation.save()
                    self.message_user(request, _("Reservation status updated."))
                    return redirect(next_url)
        else:
            default_status = (
                "accepted"
                if reservation.request_status == Reservation.RequestStatus.APPROVED
                else "denied"
            )
            status = request.GET.get("status", default_status)
            denial_reason = reservation.denial_reason

        context = {
            **self.admin_site.each_context(request),
            "title": _("Change reservation status"),
            "reservation": reservation,
            "opts": self.model._meta,
            "selected_status": status,
            "denial_reason": denial_reason,
            "error": error,
            "next": next_url,
        }
        return render(
            request, "admin/reservations/reservation/evaluate.html", context
        )

    @admin.display(description=_("Evaluation"))
    def evaluation_actions(self, request, obj):
        """Render the accept/deny/change row actions for a reservation.

        For a pending row, Accept submits the standalone form the change-list
        template renders for that row (outside the changelist's own bulk-action
        form) via the HTML ``form`` attribute, so it applies without leaving the
        page; Deny needs a reason, so it goes to the evaluate page instead. Already
        evaluated rows just get a Change link to that same evaluate page.
        """
        evaluate_url = reverse(
            "admin:reservations_reservation_evaluate", args=[obj.pk]
        )
        next_url = request.get_full_path()

        if obj.request_status == Reservation.RequestStatus.PENDING:
            deny_qs = urlencode({"status": "denied", "next": next_url})
            return format_html(
                '<button type="submit" form="reservation-accept-{0}" style="{1}">'
                "{2}</button> | "
                '<a href="{3}?{4}">{5}</a>',
                obj.pk,
                self._LINK_BUTTON_STYLE,
                _("Accept"),
                evaluate_url,
                deny_qs,
                _("Deny"),
            )

        change_qs = urlencode({"next": next_url})
        return format_html(
            '<a href="{0}?{1}">{2}</a>', evaluate_url, change_qs, _("Change")
        )
