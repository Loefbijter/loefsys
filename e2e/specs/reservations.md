# Reservations

**As a member, I want to reserve a boat or a room, so that it is available when I need
it.**

- **RES-1** The reservations page lists the member's own reservations, and nobody
  else's.
- **RES-2** A member picks a period and a room, gives a reason and reserves it; the
  reservation shows up as pending ("In behandeling") with that reason.
- **RES-10** The reason is required: without one the reservation isn't made.
- **RES-3** Choosing a location (BK, Bastion, Kraaij, Overige) shows the items kept
  there.
- **RES-4** Reserving a boat that needs a skippership asks for a skipper; the chosen
  skipper is stored on the reservation.
- **RES-9** The same works on a phone: the "Reserveren" button can be reached and
  pressed.
- **RES-5** An item that is already reserved for an overlapping period can't be
  reserved; the form says why.

**As a member, I want to cancel my reservation when plans change.**

- **RES-6** A member deletes their own reservation after confirming.

**As a member, I expect my reservations to be private to me and the board.**

- **RES-7** Another member's reservation can't be opened (not found).
- **RES-8** Another member's reservation can't be deleted.
  *Known bug: the delete view doesn't check the owner, so any member can delete any
  reservation by its number.*

Accepting and denying reservations is in [admin.md](admin.md).
