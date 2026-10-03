from io import BytesIO

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G
from openpyxl import load_workbook

from loefsys.home.models import Announcement


class AdminExportTestCase(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com", password="password"
        )
        self.client.force_login(self.admin_user)

    def test_export_filtered_rows_respects_admin_filters(self):
        G(
            Announcement,
            title="Published announcement",
            content="Visible announcement",
            published=True,
        )
        G(
            Announcement,
            title="Draft announcement",
            content="Hidden announcement",
            published=False,
        )

        response = self.client.get(
            reverse("admin:home_announcement_export_excel"), {"published": "1"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        workbook = load_workbook(
            filename=BytesIO(response.content), read_only=True, data_only=True
        )
        sheet = workbook.active
        rows = list(sheet.values)

        self.assertEqual(rows[0][0], "Id")
        self.assertEqual(rows[0][1], "Title")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][1], "Published announcement")
