# Admin roles

The activity manager and "Admin" permission criteria cover PR #175. Their tests skip
themselves while that PR isn't merged.

**As a member without any permissions, I don't get into the admin.**

- **ADM-1** Logging in to the admin is refused with an error.

**As a board member handling reservations, I want to accept or deny requests quickly.**

- **ADM-2** An admin accepts a pending reservation straight from the reservation list.
- **ADM-3** An admin denies a reservation and gives a reason, which is stored.
- **ADM-11** The "To do" on the home page takes an admin to the pending requests in the
  admin, where they can accept them (not to a page that is only for the requester).

**As an activity manager, I want to manage the activities in my categories, without
seeing other members' data.**

- **ADM-4** An activity manager gets into the admin and only sees the events part.
- **ADM-5** When adding an activity they can only pick the categories they manage.
- **ADM-6** Activities in other categories are hidden from them.
- **ADM-7** On their activities they see each registration's name, email address and
  phone number, read-only.
- **ADM-10** When the activity has extra questions, each registration can be folded out
  to read its answers.
- **ADM-8** They can't open the member list.

**As the board, I want to give someone admin access by permission instead of a staff
flag.**

- **ADM-9** The "Admin" permission alone lets a member into the admin.
