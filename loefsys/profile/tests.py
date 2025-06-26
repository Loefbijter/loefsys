# TODO Move all tests into a module instead of a single file.
"""Module defining the tests for profile."""

import io
import os
import shutil
from datetime import date
from pathlib import Path

from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django_dynamic_fixture import G

from loefsys.groups.models import LoefbijterGroup
from loefsys.members.models import MemberDetails, Membership, User

settings.LANGUAGE_CODE = "en"


class LoginTestCase(TestCase):
    """Tests for signing up and logging in."""

    def setUp(self):
        """Set up the needed variables for the tests."""
        self.client = Client()
        self.email = "user@user.nl"
        self.new_email = "new.user@email.com"
        self.password = "password"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            phone_number="+31612345678",
            nickname="Naam",
            picture=None,
        )

    def test_login_page(self):
        """Tests if the login page is rightfully loaded."""
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Login")

    def test_invalid_credentials_login(self):
        """Tests if invalid credentails are rightfully handled."""
        form_data_wrong_email = {
            "username": "notuser@user.nl",
            "password": self.password,
        }
        form_data_wrong_password = {
            "username": self.email,
            "password": "notthepassword",
        }
        response = self.client.post(
            reverse("login"), data=form_data_wrong_email, follow=True
        )
        self.assertContains(response, "Please enter a correct email and password.")

        response = self.client.post(
            reverse("login"), data=form_data_wrong_password, follow=True
        )
        self.assertContains(response, "Please enter a correct email and password.")

    def test_login(self):
        """Tests if a user can login."""
        form_data = {"username": self.email, "password": self.password}
        response = self.client.post(reverse("login"), data=form_data, follow=True)
        user = response.context["user"]
        self.assertTrue(user.is_authenticated)

    def test_signup_existing_acc(self):
        """Tests that you can not sign up with an existing email."""
        form_data = {
            "email": self.email,
            "password1": "DiffPass!",
            "password2": "DiffPass!",
        }
        response = self.client.post(reverse("signup"), data=form_data, follow=True)
        self.assertContains(response, "User with this Email already exists.")
        self.assertTrue(self.user)

    def test_signup_invalid_password(self):
        """Tests that you can not sign up with an inval password."""
        form_data_personal_info = {
            "email": self.new_email,
            "password1": self.new_email,
            "password2": self.new_email,
        }

        form_data_short = {
            "email": self.new_email,
            "password1": "short",
            "password2": "short",
        }
        form_data_common = {
            "email": self.new_email,
            "password1": "password123",
            "password2": "password123",
        }
        form_data_num = {
            "email": self.new_email,
            "password1": "759268743605729084",
            "password2": "759268743605729084",
        }

        response = self.client.post(
            reverse("signup"), data=form_data_personal_info, follow=True
        )
        self.assertContains(response, "The password is too similar to the email.")

        response = self.client.post(
            reverse("signup"), data=form_data_short, follow=True
        )
        self.assertContains(
            response,
            "This password is too short. It must contain at least 8 characters.",
        )

        response = self.client.post(
            reverse("signup"), data=form_data_common, follow=True
        )
        self.assertContains(response, "This password is too common.")

        response = self.client.post(reverse("signup"), data=form_data_num, follow=True)
        self.assertContains(response, "This password is entirely numeric.")

    def test_signup_diff_password(self):
        """Tests that if you enter 2 different passwords it denies the request."""
        form_data = {
            "email": self.new_email,
            "password1": self.password,
            "password2": "Diffpass!",
        }
        response = self.client.post(reverse("signup"), data=form_data, follow=True)
        self.assertContains(response, "The two password fields didn’t match.")  # noqa: RUF001

    def test_signup(self):
        """Test for when a valid signup is performed, a user is created."""
        user = get_user_model()

        # check that user does not exist at first
        self.assertFalse(user.objects.filter(email="user2@user.com").exists())

        form_data = {
            "email": "user2@user.com",
            "first_name": "Voornaam",
            "last_name": "Achternaam",
            "phone_number": "+31612345678",
            "password1": "Hardpassword#2",
            "password2": "Hardpassword#2",
        }

        self.client.post(reverse("signup"), data=form_data, follow=True)

        self.assertTrue(user.objects.filter(email="user2@user.com").exists())


class EditAccountInformationTestCase(TestCase):
    """Tests for account information modification for users."""

    def setUp(self):
        """Set up users and constants."""
        self.client = Client()
        self.user = G(
            User,
            email="user@user.nl",
            password="secret1",
            phone_number="+31612345678",
            nickname="A",
            picture=None,
        )
        self.member = G(
            MemberDetails, user=self.user, birthday=date(2004, 1, 1), show_birthday=True
        )
        self.membership = G(Membership, member=self.member, start=date(2024, 1, 1))
        self.edit_url = reverse("accountinfoedit")
        self.upload_path = Path(settings.MEDIA_ROOT) / self.user.user_upload_directory()

    def tearDown(self):
        """Clean up method after tests are done."""
        # Clean up the upload folder
        if os.path.exists(self.upload_path):
            shutil.rmtree(self.upload_path)

    def create_image(self):
        """Create a test image."""
        # Create a small image in memory
        image_file = io.BytesIO()
        image = Image.new(
            "RGB", (100, 100), color=(255, 0, 0)
        )  # Create a red 100x100 image
        image.save(image_file, format="JPEG")
        image_file.seek(0)  # Move the pointer back to the beginning of the file
        return image_file

    def test_valid_form_submitted(self):
        """Test for when a valid form is submitted.

        The data should be changed.
        """
        form_data = {
            "phone_number": "+31612345000",
            "nickname": self.user.nickname,
            "display_name_preference": self.user.display_name_preference,
            "birthday": date(2003, 1, 1),
            "gender": self.member.gender,
            "show_birthday": self.member.show_birthday,
        }
        self.client.force_login(user=self.user)
        response = self.client.post(reverse("accountinfoedit"), data=form_data)
        self.assertEqual(response.status_code, 302)  # expect redirect to account page
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response=response, text="+31612345000")
        self.assertContains(response=response, text="2003-01-01")

    def test_invalid_form_submitted(self):
        """Test for when an invalid form is submitted.

        The data should not be changed (user form is incorrect, member form is okay).
        """
        form_data = {
            "phone_number": "+316123450001",
            "nickname": self.user.nickname,
            "display_name_preference": self.user.display_name_preference,
            "birthday": date(2003, 1, 1),
            "gender": self.member.gender,
            "show_birthday": self.member.show_birthday,
        }
        self.client.force_login(user=self.user)
        response = self.client.post(reverse("accountinfoedit"), data=form_data)
        self.assertEqual(response.status_code, 200)  # expect to load same page again
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response=response, text="+316123450001")
        self.assertContains(response=response, text="+31612345678")
        self.assertNotContains(response=response, text="2003-01-01")
        self.assertContains(response=response, text="2004-01-01")

    def test_invalid_form_submitted_2(self):
        """Test for when an invalid form is submitted.

        The data should not be changed (user form is okay, member form is incorrect).
        """
        form_data = {
            "phone_number": "+31612345000",
            "nickname": self.user.nickname,
            "display_name_preference": self.user.display_name_preference,
            "birthday": date(2003, 1, 1),
            "show_birthday": self.member.show_birthday,
        }
        self.client.force_login(user=self.user)
        response = self.client.post(reverse("accountinfoedit"), data=form_data)
        self.assertEqual(response.status_code, 200)  # expect to load same page again
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response=response, text="+31612345000")
        self.assertContains(response=response, text="+31612345678")
        self.assertNotContains(response=response, text="2003-01-01")
        self.assertContains(response=response, text="2004-01-01")

    def test_user_picture(self):
        """Test for when the profile picture is updated and cleared.

        Check that when the picture is updated, the new picture is displayed
        instead of the default picture, and when the picture is cleared, the
        default picture is displayed again.
        """
        self.client.force_login(user=self.user)
        response = self.client.get("/profile/")
        self.assertContains(response=response, text="Default_pfp.png")
        image_file = self.create_image()
        image = SimpleUploadedFile(
            name="picture.jpg", content=image_file.read(), content_type="image/jpeg"
        )
        form_data = {
            "phone_number": self.user.phone_number,
            "nickname": self.user.nickname,
            "display_name_preference": self.user.display_name_preference,
            "birthday": self.member.birthday,
            "show_birthday": self.member.show_birthday,
            "gender": self.member.gender,
            "picture": image,
        }
        response = self.client.post(reverse("accountinfoedit"), data=form_data)
        self.assertEqual(response.status_code, 302)  # expect redirect to account page
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response=response, text="picture.jpg")
        form_data = {
            "phone_number": self.user.phone_number,
            "nickname": self.user.nickname,
            "display_name_preference": self.user.display_name_preference,
            "birthday": self.member.birthday,
            "show_birthday": self.member.show_birthday,
            "gender": self.member.gender,
            "picture-clear": "on",
        }
        response = self.client.post(reverse("accountinfoedit"), data=form_data)
        self.assertEqual(response.status_code, 302)  # expect redirect to account page
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response=response, text="Default_pfp.png")

    def test_delete_account(self):
        """Tests if the user account is deleted when a user clicks the button."""
        self.client.force_login(user=self.user)
        delete_url = reverse("delete_account")
        response = self.client.post(delete_url, follow=True)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.user.pk)
        self.assertRedirects(response, reverse("login"))


class UserTestCase(TestCase):
    """Tests for the account information display for users."""

    def setUp(self):
        """Set up user without groups and user with groups."""
        self.client = Client()
        self.user1 = G(
            User, email="user@user.nl", password="secret1", phone_number="+31612345678"
        )

        self.group1 = G(
            LoefbijterGroup,
            name="Title",
            description="Description",
            date_foundation=date(2021, 1, 1),
            display_members=False,
        )
        self.group2 = G(
            LoefbijterGroup,
            name="Board",
            description="58e",
            date_foundation=date(2021, 1, 1),
            display_members=False,
        )
        self.user2 = G(
            User,
            email="user2@user2.nl",
            password="secret2",
            phone_number="+31612345678",
            groups=[self.group1, self.group2],
        )

    def not_logged_in(self):
        """Test for when a user is not logged in.

        The user should be redirected to the signup page.
        """
        response = self.client.get("/profile/")
        self.assertRedirects(
            response=response, expected_url="/signup/", status_code=301
        )

    def test_user_without_groups(self):
        """Test for when a user is not part of any groups.

        All user information should be displayed, apart from groups.
        """
        self.client.force_login(user=self.user1)
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response=response, text="user@user.nl")
        self.assertContains(response=response, text="+31612345678")
        self.assertNotContains(response=response, text="Member")
        self.assertNotContains(response=response, text="My groups")

    def test_user_with_groups(self):
        """Test for when a user is a part of groups.

        All the groups should be displayed.
        """
        self.client.force_login(user=self.user2)
        response = self.client.get("/profile/")
        self.assertContains(response=response, text="Mijn groepen")
        self.assertContains(response=response, text="Title")
        self.assertContains(response=response, text="Description")
        self.assertContains(response=response, text="Board")
        self.assertContains(response=response, text="58e")


class MemberTestCase(TestCase):
    """Tests for the account information display for members."""

    def setUp(self):
        """Set up member."""
        self.user = G(
            User,
            email="member@member.nl",
            password="secret",
            phone_number="+31687654321",
        )
        self.member = G(
            MemberDetails, user=self.user, birthday=date(2004, 1, 1), show_birthday=True
        )

    def test_member(self):
        """Test for when a user is a member.

        All member information should be displayed.
        """
        G(Membership, member=self.member, start=date(2024, 1, 1))

        self.client.force_login(user=self.user)
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response=response, text="member@member.nl")
        self.assertContains(response=response, text="+31687654321")
        self.assertContains(response=response, text="Member")
        self.assertContains(response=response, text="2004-01-01")
        self.assertContains(response=response, text="2024-01-01")

    def test_member_without_membership(self):
        """Test for when a member has no membership.

        An exception should be raised.
        """
        self.client.force_login(user=self.user)
        with self.assertRaises(
            expected_exception=Exception, msg="Member has no membership"
        ):
            self.client.get("/profile/")

    def test_member_with_multiple_memberships(self):
        """Test for when a member has multiple memberships.

        The latest membership information should be displayed.
        """
        G(Membership, member=self.member, start=date(2022, 1, 1))
        G(Membership, member=self.member, start=date(2023, 1, 1))

        self.client.force_login(user=self.user)
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response=response, text="2022-01-01")
        self.assertContains(response=response, text="2023-01-01")
