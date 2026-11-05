from django.db import migrations
from django.db.models.functions import Lower

import loefsys.members.models.fields


def lowercase_emails(apps, schema_editor):
    """Store every email address in lowercase.

    Fails, without changing anything, when two accounts differ only in the case of
    their address: those need to be merged or changed by hand first.
    """
    user_model = apps.get_model("members", "User")
    addresses: dict[str, list[str]] = {}
    for email in user_model.objects.values_list("email", flat=True):
        addresses.setdefault(email.lower(), []).append(email)
    clashes = [found for found in addresses.values() if len(found) > 1]
    if clashes:
        listing = "; ".join(", ".join(found) for found in clashes)
        raise RuntimeError(
            "Accounts whose email addresses differ only in case must be merged or "
            f"changed before this migration: {listing}"
        )
    user_model.objects.update(email=Lower("email"))


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0010_remove_userskippership_given_by"),
    ]

    operations = [
        migrations.RunPython(lowercase_emails, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=loefsys.members.models.fields.LowercaseEmailField(
                max_length=254, unique=True, verbose_name="Email address"
            ),
        ),
    ]
