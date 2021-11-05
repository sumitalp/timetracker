class TeamStatus:
    ACTIVE = 1
    DELETED = 2

    CHOICES = (
        (ACTIVE, "Active"),
        (DELETED, "Deleted"),
    )


class InviteStatus:
    INVITED = 1
    ACCEPTED = 2

    CHOICES = (
        (INVITED, "Invited"),
        (ACCEPTED, "Accepted"),
    )
    